import pytest
from pydantic import ValidationError

from edenai_apis.features.text.sentiment_analysis.sentiment_analysis_dataclass import (
    SegmentSentimentAnalysisDataClass,
    SentimentEnum,
    SentimentAnalysisDataClass,
)

FEATURE = "text"
SUBFEATURE = "sentiment_analysis"


def _assign_markers_parametrize(expected, **kwargs):
    return pytest.param(
        kwargs,
        expected,
        marks=[getattr(pytest.mark, FEATURE), getattr(pytest.mark, SUBFEATURE)],
    )


class TestSegmentSentimentAnalysisDataClass:
    @pytest.mark.parametrize(
        ("kwargs", "expected"),
        [
            _assign_markers_parametrize(
                segment="Valid segment",
                sentiment=SentimentEnum.POSITIVE.value,
                sentiment_rate=0,
                expected={"sentiment": "Positive", "sentiment_rate": 0.00},
            ),
            _assign_markers_parametrize(
                segment="Valid segment",
                sentiment=SentimentEnum.NEGATIVE.value,
                sentiment_rate=1.0,
                expected={"sentiment": "Negative", "sentiment_rate": 1.00},
            ),
            _assign_markers_parametrize(
                segment="Valid segment",
                sentiment=SentimentEnum.NEUTRAL.value,
                sentiment_rate=0.578,
                expected={"sentiment": "Neutral", "sentiment_rate": 0.58},
            ),
            _assign_markers_parametrize(
                segment="Valid segment",
                sentiment="neutral",
                sentiment_rate=None,
                expected={"sentiment": "Neutral", "sentiment_rate": None},
            ),
        ],
        ids=[
            "test_with_sentiment_positive_enum_rate_0",
            "test_with_sentiment_negative_enum_rate_1.00",
            "test_with_sentiment_neutral_enum_rate_0.578",
            "test_with_sentiment_neutral_rate_none",
        ],
    )
    def test_valid_input(self, kwargs, expected):
        expected["segment"] = kwargs["segment"]

        segment_sentiment_class = SegmentSentimentAnalysisDataClass(**kwargs)

        assert (
            segment_sentiment_class.segment == expected["segment"]
        ), "The value of `segment` must not change during the assignment"

        assert (
            segment_sentiment_class.sentiment == expected["sentiment"]
        ), "The value of `sentiment` must be in ['Positive', 'Negative', 'Neutral']"

        assert (
            segment_sentiment_class.sentiment_rate == expected["sentiment_rate"]
        ), "The value of `sentiment_rate` must be rounded to the hundredth"

    @pytest.mark.parametrize(
        ("kwargs", "expected"),
        [
            _assign_markers_parametrize(
                segment="Valid segment",
                sentiment="invalid sentiment",
                sentiment_rate=0,
                expected={
                    'invalid_field': 'sentiment',
                    "raise_type": ValueError,
                    "raise_message": "Sentiment must be 'Positive' or 'Negative' or 'Neutral'",
                },
            ),
            _assign_markers_parametrize(
                segment="Valid segment",
                sentiment=1,
                sentiment_rate=0,
                expected={
                    "invalid_field": 'sentiment',
                    "raise_type": ValueError,
                    "raise_message": "Sentiment must be a string",
                },
            ),
            _assign_markers_parametrize(
                segment=1,
                sentiment="Positive",
                sentiment_rate=0,
                expected={
                    "invalid_field": 'segment',
                    "raise_type": ValueError,
                    "raise_message": "Segment must be a string",
                },
            ),
            _assign_markers_parametrize(
                segment="Valid segment",
                sentiment=SentimentEnum.POSITIVE.value,
                sentiment_rate="0",
                expected={
                    'invalid_field': 'sentiment_rate',
                    "raise_type": ValueError,
                    "raise_message": "Sentiment rate must be a float",
                },
            ),
        ],
        ids=[
            "test_with_bad_sentiment_format",
            "test_with_non_str_sentiment",
            "test_with_non_str_segment",
            "test_with_non_number_rate",
            # "test_with_min_overflow_rate",
            # "test_with_max_overflow_rate",
        ],
    )
    def test_invalid_input(self, kwargs, expected):
        segment_sentiment_class = SegmentSentimentAnalysisDataClass(**kwargs)
        assert getattr(segment_sentiment_class, expected['invalid_field']) is None


class TestSentimentAnalysisDataClass:
    ITEMS = [
        SegmentSentimentAnalysisDataClass(
            segment="Valid Segement", sentiment="Positive", sentiment_rate=0.5
        )
    ]

    @pytest.mark.parametrize(
        ("kwargs", "expected"),
        [
            _assign_markers_parametrize(
                items=ITEMS,
                general_sentiment=SentimentEnum.POSITIVE.value,
                general_sentiment_rate=0,
                expected={"sentiment": "Positive", "sentiment_rate": 0.00},
            ),
            _assign_markers_parametrize(
                items=ITEMS,
                general_sentiment=SentimentEnum.NEGATIVE.value,
                general_sentiment_rate=1.0,
                expected={"sentiment": "Negative", "sentiment_rate": 1.00},
            ),
            _assign_markers_parametrize(
                items=ITEMS,
                general_sentiment=SentimentEnum.NEUTRAL.value,
                general_sentiment_rate=0.578,
                expected={"sentiment": "Neutral", "sentiment_rate": 0.58},
            ),
            _assign_markers_parametrize(
                items=ITEMS,
                general_sentiment="neutral",
                general_sentiment_rate=None,
                expected={"sentiment": "Neutral", "sentiment_rate": None},
            ),
        ],
        ids=[
            "test_with_sentiment_positive_enum_rate_0",
            "test_with_sentiment_negative_enum_rate_1.00",
            "test_with_sentiment_neutral_enum_rate_0.578",
            "test_with_sentiment_neutral_rate_none",
        ],
    )
    def test_valid_input(self, kwargs, expected):
        klass = SentimentAnalysisDataClass(**kwargs)

        assert (
            klass.general_sentiment == expected["sentiment"]
        ), "The value of `sentiment` must be in ['Positive', 'Negative', 'Neutral']"

        assert (
            klass.general_sentiment_rate == expected["sentiment_rate"]
        ), "The value of `sentiment_rate` must be rounded to the hundredth"

    ## TODO: Fix this test
    # @pytest.mark.parametrize(
    #     ("kwargs", "expected"),
    #     [
    #         _assign_markers_parametrize(
    #             items=ITEMS,
    #             general_sentiment="invalid sentiment",
    #             general_sentiment_rate=0,
    #             expected={
    #                 "raise_type": ValueError,
    #                 "raise_message": "General sentiment must be 'Positive' or 'Negative' or 'Neutral'",
    #             },
    #         ),
    #         _assign_markers_parametrize(
    #             items=ITEMS,
    #             general_sentiment=1,
    #             general_sentiment_rate=0,
    #             expected={
    #                 "raise_type": TypeError,
    #                 "raise_message": "General sentiment must be a string",
    #             },
    #         ),
    #         _assign_markers_parametrize(
    #             items=ITEMS,
    #             general_sentiment=SentimentEnum.POSITIVE.value,
    #             general_sentiment_rate="0",
    #             expected={
    #                 "raise_type": TypeError,
    #                 "raise_message": "General sentiment rate must be a float",
    #             },
    #         ),
    #         _assign_markers_parametrize(
    #             items=ITEMS,
    #             general_sentiment=SentimentEnum.POSITIVE.value,
    #             general_sentiment_rate=-1,
    #             expected={
    #                 "raise_type": ValidationError,
    #                 "raise_message": re.escape(
    #                     "1 validation error for SentimentAnalysisDataClass\ngeneral_sentiment_rate\n  ensure this value is greater than or equal to 0 (type=value_error.number.not_ge; limit_value=0)"
    #                 ),
    #             },
    #         ),
    #         _assign_markers_parametrize(
    #             items=ITEMS,
    #             general_sentiment=SentimentEnum.POSITIVE.value,
    #             general_sentiment_rate=2,
    #             expected={
    #                 "raise_type": ValidationError,
    #                 "raise_message": re.escape(
    #                     "1 validation error for SentimentAnalysisDataClass\ngeneral_sentiment_rate\n  ensure this value is less than or equal to 1 (type=value_error.number.not_le; limit_value=1)"
    #                 ),
    #             },
    #         ),
    #     ],
    #     ids=[
    #         "test_with_bad_sentiment_format",
    #         "test_with_non_str_sentiment",
    #         "test_with_non_number_rate",
    #         "test_with_min_overflow_rate",
    #         "test_with_max_overflow_rate",
    #     ],
    # )
    # def test_invalid_input(self, kwargs, expected):
    #     with pytest.raises(
    #         (expected["raise_type"], ValidationError), match=expected["raise_message"]
    #     ):
    #         klass = SentimentAnalysisDataClass(**kwargs)
