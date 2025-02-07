# pylint: disable=locally-disabled, too-many-branches
import os
import random
import time
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Type, Union, overload
from uuid import uuid4

from edenai_apis import interface_v2
from edenai_apis.features.provider.provider_interface import ProviderInterface
from edenai_apis.loaders.data_loader import FeatureDataEnum, ProviderDataEnum
from edenai_apis.loaders.loaders import load_feature, load_provider
from edenai_apis.utils.constraints import validate_all_provider_constraints
from edenai_apis.utils.exception import ProviderException, get_appropriate_error
from edenai_apis.utils.monitoring import insert_api_call, monitor_call
from edenai_apis.utils.types import AsyncLaunchJobResponseType
from dotenv import load_dotenv

load_dotenv()
IS_MONITORING = os.environ.get("MONITORING") is not None  # see utils.monitoring

ProviderDict = Dict[
    str, Dict[str, Dict[str, Union[Dict[str, Literal[True]], Literal[True]]]]
]
FeatureSubfeatureProviderTuple = Union[Tuple[str, str, str], Tuple[str, str, str, str]]
ProviderList = List[FeatureSubfeatureProviderTuple]


@overload
def list_features(
    provider_name: Optional[str] = None,
    feature: Optional[str] = None,
    subfeature: Optional[str] = None,
    as_dict: Literal[False] = False,
) -> ProviderList:
    ...


@overload
def list_features(
    provider_name: Optional[str] = None,
    feature: Optional[str] = None,
    subfeature: Optional[str] = None,
    as_dict: Literal[True] = True,
) -> ProviderDict:
    ...


def list_features(
    provider_name: Optional[str] = None,
    feature: Optional[str] = None,
    subfeature: Optional[str] = None,
    as_dict: bool = False,
) -> Union[ProviderList, ProviderDict]:
    """
    Gets all possible provider/feature/subfeature or provider/feature/subfeature/phase as a list if `as_dict` is `False`,
    otherwise returns the resutls as a dict.

    Example of dict result:
    ```python
    {
        [provider]: {
            [feature]: {
                [subfeature]: True
            }
        }
    }
    ```
    or if phase is present
    ```python
    {
        [provider]: {
            [feature]: {
                [subfeature]: {
                    [phase] : True
                }
            }
        }
    }
    ```

    Examples list result:
    ```python
    [(provider, feature, subfeature, phase), (provider, feature, subfeature, phase), ...]
    ```
    or
    ```python
    [(provider, feature, subfeature), (provider, feature, subfeature), ...]
    ```

    Args:
        provider_name (str, optional): Eden AI provider name. Defaults to None.
        feature (str, optional): Eden AI feature name. Defaults to None.
        subfeature (str, optional): Eden AI subfeature name. Defaults to None.
        as_dict (bool, optional): Whether or not return the results as a Dict. Defaults to False.

    Returns:
        (list | dict): Return all possible provider/feature/subfeature or provider/feature/subfeature/phase as a list or dict
    """

    method_set: Set[FeatureSubfeatureProviderTuple] = set()
    ApiClasses: List[Type[ProviderInterface]] = load_provider(ProviderDataEnum.CLASS)
    for cls in ApiClasses:
        if (
            not provider_name or cls.provider_name == provider_name
        ):  # filter for provider_name if provided
            # detect feature,subfeature,phase by looking at methods names
            for method_name in filter(
                lambda method_name: not method_name.startswith("_")
                and "__" in method_name
                and getattr(getattr(cls, method_name), "__isabstractmethod__", False)
                is False,  # do not include method that are not implemented yet (interfaces abstract methods)
                dir(cls),
            ):
                feature_i, subfeature_i, *others = method_name.split("__")
                if not (feature or feature == feature_i) and not (
                    subfeature or subfeature == subfeature_i
                ):  # filter by subfeature if provided
                    if len(others) > 0 and "async" not in subfeature_i:
                        phase = others[0]
                        method_set.add(
                            (cls.provider_name, feature_i, subfeature_i, phase)
                        )
                    else:
                        method_set.add((cls.provider_name, feature_i, subfeature_i))
    method_list: ProviderList = list(method_set)
    method_list.sort()
    if not as_dict:
        return method_list  # return a list

    # return resutls as dict
    result = {}
    for provider, feature_i, subfeature_i, *phase in method_list:
        if provider not in result:
            result[provider] = {}
        if feature_i not in result[provider]:
            result[provider][feature_i] = {}
        have_phases = isinstance(result[provider][feature_i].get(subfeature_i), dict)
        if result[provider][feature_i].get(subfeature_i) is None or have_phases:
            if phase:
                if not have_phases:
                    result[provider][feature_i][subfeature_i] = {}
                if not phase[0] in result[provider][feature_i][subfeature_i]:
                    result[provider][feature_i][subfeature_i][phase[0]] = True
            else:
                result[provider][feature_i][subfeature_i] = True

    return result


def list_providers(
    feature: Optional[str] = None, subfeature: Optional[str] = None
) -> List[str]:
    """
    Lists all providers that implement the given feature/subfeature

    Args:
        feature(str, optional): Edenai AI feature name. Default to `None`.
        subfeature(str, optional): Edenai AI subfeature name. Default to `None`.

    Returns:
        List[str]: list of provider names
    """
    # TO DO: keep the set as output, don't convert to list
    providers_set = set()
    for provider, feature_i, subfeature_i, *_phase in list_features():
        if not feature or feature_i == feature:
            if not subfeature or subfeature_i == subfeature:
                providers_set.add(provider)
    return list(providers_set)


STATUS_SUCCESS = "success"


@monitor_call(condition=IS_MONITORING)
def compute_output(
    provider_name: str,
    feature: str,
    subfeature: str,
    args: Dict[str, Any],
    phase: str = "",
    fake: bool = False,
    api_keys: Dict = {},
    user_email: Optional[str] = None,
) -> Dict:
    """
    Compute subfeature for provider and subfeature

    Args:
        provider_name (str): EdenAI provider name
        feature (str): EdenAI feature name
        subfeature (str): EdenAI subfeature name
        phase (str): Eden AI phase name if give, Default to `Literal[""]`
        args (Dict): inputs arguments for the feature call
        fake (bool, optional): take result from sample. Defaults to `False`.
        api_keys (dict, optional): optional user's api_keys for each providers
        user_email (str, optional): optinal user email for monitoring (opted-out by default)

    Returns:
        dict: Result dict
    """
    # check if the function we're running is asyncronous
    is_async = ("_async" in phase) if phase else ("_async" in subfeature)
    # suffix is used for async
    suffix = "__launch_job" if is_async else ""

    # if language input, update args with a standardized language
    args = validate_all_provider_constraints(
        provider_name, feature, subfeature, phase, args
    )

    if fake:
        time.sleep(
            random.uniform(0.5, 1.5)
        )  # sleep to fake the response time from a provider
        # sample_args = load_feature(
        #     FeatureDataEnum.SAMPLES_ARGS,
        #     feature=feature,
        #     subfeature=subfeature,
        #     phase=phase,
        #     provider_name=provider_name,
        # )
        # replace File Wrapper by file and file_url inputs and also transform input attributes as settings for tts
        # sample_args = validate_all_provider_constraints(
        #     provider_name, feature, subfeature, phase, sample_args
        # )

        # Return mocked results
        if is_async:
            subfeature_result: Any = AsyncLaunchJobResponseType(
                provider_job_id=str(uuid4())
            ).model_dump()
        # TODO: refacto image search to save output with this phase
        elif phase in ["upload_image", "delete_image"]:
            subfeature_result = {"status": STATUS_SUCCESS}
        else:
            subfeature_result = load_provider(
                ProviderDataEnum.OUTPUT,
                provider_name=provider_name,
                feature=feature,
                subfeature=subfeature,
                phase=phase,
            )

    else:
        # Fake == False : Compute real output

        feature_class = getattr(interface_v2, feature.title())
        subfeature_method_name = f'{subfeature}{f"__{phase}" if phase else ""}{suffix}'
        subfeature_class = getattr(feature_class, subfeature_method_name)

        try:
            subfeature_result = subfeature_class(provider_name, api_keys)(
                **args
            ).model_dump()
        except ProviderException as exc:
            raise get_appropriate_error(provider_name, exc)

    final_result: Dict[str, Any] = {
        "status": STATUS_SUCCESS,
        "provider": provider_name,
        **subfeature_result,
    }

    if os.environ.get("MONITORING", False) is True and user_email:
        error = "Fake" if fake else None
        insert_api_call(
            provider=provider_name,
            feature=feature,
            subfeature=subfeature,
            user_email=user_email,
            error=error,
        )

    return final_result


# HACK: Why this function is the package provider instead of the backend ?
# It only use in the backend, never in the package provider
def check_provider_constraints(
    provider_name: str,
    feature: str,
    subfeature: str,
    phase: Optional[str] = None,
    constraints: Optional[Dict] = None,
) -> Tuple[bool, str]:
    """
    Checks if provider is ok for one feature and subfeature (and phase if given)
    Check for constraints as well

    Args:
        provider_name (str): EdenAI provider name
        feature (str): only feature key.
        subfeature (str): only subfeature key.
        phase (str, optional): EdenAI phase. Defaults to `None`.
        constraints (Dict): constraints. Defaults to `None`.

    Returns:
        Tuple[bool, str]: Provider is ok, debug string
    """

    # Refacto : use list_providers ?
    subfeatures_providers = list_features(as_dict=True)
    provider_info = subfeatures_providers.get(provider_name, None)
    if not provider_info:
        return False, f"Provider : '{provider_name}' unknown."
    if feature not in provider_info:
        return (
            False,
            f"Provider : '{provider_name}' does not provide an API for '{feature} {subfeature}'",
        )
    if subfeature not in provider_info[feature]:
        return (
            False,
            f"Provider : '{provider_name}' does not provide an API for '{feature} {subfeature}'",
        )
    if phase:
        if not isinstance(provider_info[feature][subfeature], dict) or (
            isinstance(provider_info[feature][subfeature], dict)
            and phase not in provider_info[feature][subfeature].keys()
        ):
            return (
                False,
                f"Provider : '{provider_name}' does not provide an API for "
                + "'{feature} {subfeature} {phase}'",
            )

    if constraints:
        for key, values in constraints:
            for value in values:
                if (
                    not value
                    in load_provider(
                        ProviderDataEnum.PROVIDER_INFO,
                        provider_name=provider_name,
                        feature=feature,
                        subfeature=subfeature,
                        phase=phase,
                    )[key]
                ):
                    return (
                        False,
                        f"constraint : '{key} - {values}' not filled for '{provider_name}'",
                    )
    return True, "All Good!"


@monitor_call(condition=IS_MONITORING)
def get_async_job_result(
    provider_name: str,
    feature: str,
    subfeature: str,
    async_job_id: AsyncLaunchJobResponseType,
    phase: str = "",
    fake: bool = False,
    user_email=None,
    api_keys=dict(),
) -> Dict:
    """Get async result from job id

    Args:
        provider_name (str): EdenAI provider name
        feature (str): EdenAI feature
        subfeature (str): EdenAI subfeature
        async_job_id (str): async job id to get result to
        phase (str): EdenAI phase. Default to empty string ("")
        fake (bool): Load fake results

    Returns:
        Dict: Result dict
    """

    if fake is True:
        time.sleep(
            random.uniform(0.5, 1.5)
        )  # sleep to fake the response time from a provider
        # Load fake data from edenai_apis' saved output
        fake_result = load_provider(
            ProviderDataEnum.OUTPUT,
            provider_name=provider_name,
            feature=feature,
            subfeature=subfeature,
            phase=phase,
        )
        fake_result["provider_job_id"] = async_job_id

        return fake_result

    feature_class = getattr(interface_v2, feature.title())
    subfeature_method_name = (
        f'{subfeature}{f"__{phase}" if phase else ""}__get_job_result'
    )
    subfeature_class = getattr(feature_class, subfeature_method_name)

    try:
        subfeature_result = subfeature_class(provider_name, api_keys)(
            async_job_id
        ).model_dump()
    except ProviderException as exc:
        raise get_appropriate_error(provider_name, exc)

    return subfeature_result
