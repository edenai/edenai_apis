from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, Field, StrictStr


class FaceLandmarks(NoRaiseBaseModel):
    left_eye: Sequence[float] = Field(default_factory=list)
    left_eye_top: Sequence[float] = Field(default_factory=list)
    left_eye_right: Sequence[float] = Field(default_factory=list)
    left_eye_bottom: Sequence[float] = Field(default_factory=list)
    left_eye_left: Sequence[float] = Field(default_factory=list)
    right_eye: Sequence[float] = Field(default_factory=list)
    right_eye_top: Sequence[float] = Field(default_factory=list)
    right_eye_right: Sequence[float] = Field(default_factory=list)
    right_eye_bottom: Sequence[float] = Field(default_factory=list)
    right_eye_left: Sequence[float] = Field(default_factory=list)
    left_eyebrow_left: Sequence[float] = Field(default_factory=list)
    left_eyebrow_right: Sequence[float] = Field(default_factory=list)
    left_eyebrow_top: Sequence[float] = Field(default_factory=list)
    right_eyebrow_left: Sequence[float] = Field(default_factory=list)
    right_eyebrow_right: Sequence[float] = Field(default_factory=list)
    left_pupil: Sequence[float] = Field(default_factory=list)
    right_pupil: Sequence[float] = Field(default_factory=list)
    nose_tip: Sequence[float] = Field(default_factory=list)
    nose_bottom_right: Sequence[float] = Field(default_factory=list)
    nose_bottom_left: Sequence[float] = Field(default_factory=list)
    mouth_left: Sequence[float] = Field(default_factory=list)
    mouth_right: Sequence[float] = Field(default_factory=list)
    right_eyebrow_top: Sequence[float] = Field(default_factory=list)
    midpoint_between_eyes: Sequence[float] = Field(default_factory=list)
    nose_bottom_center: Sequence[float] = Field(default_factory=list)
    nose_left_alar_out_tip: Sequence[float] = Field(default_factory=list)
    nose_left_alar_top: Sequence[float] = Field(default_factory=list)
    nose_right_alar_out_tip: Sequence[float] = Field(default_factory=list)
    nose_right_alar_top: Sequence[float] = Field(default_factory=list)
    nose_root_left: Sequence[float] = Field(default_factory=list)
    nose_root_right: Sequence[float] = Field(default_factory=list)
    upper_lip: Sequence[float] = Field(default_factory=list)
    under_lip: Sequence[float] = Field(default_factory=list)
    under_lip_bottom: Sequence[float] = Field(default_factory=list)
    under_lip_top: Sequence[float] = Field(default_factory=list)
    upper_lip_bottom: Sequence[float] = Field(default_factory=list)
    upper_lip_top: Sequence[float] = Field(default_factory=list)
    mouth_center: Sequence[float] = Field(default_factory=list)
    mouth_top: Sequence[float] = Field(default_factory=list)
    mouth_bottom: Sequence[float] = Field(default_factory=list)
    left_ear_tragion: Sequence[float] = Field(default_factory=list)
    right_ear_tragion: Sequence[float] = Field(default_factory=list)
    forehead_glabella: Sequence[float] = Field(default_factory=list)
    chin_gnathion: Sequence[float] = Field(default_factory=list)
    chin_left_gonion: Sequence[float] = Field(default_factory=list)
    chin_right_gonion: Sequence[float] = Field(default_factory=list)
    upper_jawline_left: Sequence[float] = Field(default_factory=list)
    mid_jawline_left: Sequence[float] = Field(default_factory=list)
    mid_jawline_right: Sequence[float] = Field(default_factory=list)
    upper_jawline_right: Sequence[float] = Field(default_factory=list)
    left_cheek_center: Sequence[float] = Field(default_factory=list)
    right_cheek_center: Sequence[float] = Field(default_factory=list)


class FaceEmotions(NoRaiseBaseModel):
    joy: Optional[int]  # all
    sorrow: Optional[int]  # all
    anger: Optional[int]  # all
    surprise: Optional[int]  # all
    disgust: Optional[int]  # amazon, microsoft
    fear: Optional[int]  # amazon, microsoft
    confusion: Optional[int]  # amazon
    calm: Optional[int]  # amazon
    unknown: Optional[int]  # amazon
    neutral: Optional[int]  # microsoft
    contempt: Optional[int]  # microsoft

    @staticmethod
    def default() -> "FaceEmotions":
        return FaceEmotions(
            joy=None,
            sorrow=None,
            anger=None,
            surprise=None,
            disgust=None,
            fear=None,
            confusion=None,
            calm=None,
            unknown=None,
            neutral=None,
            contempt=None,
        )


class FaceHairColor(NoRaiseBaseModel):
    color: StrictStr
    confidence: float


class FaceHair(NoRaiseBaseModel):
    hair_color: Sequence[FaceHairColor] = Field(default_factory=list)  # microsoft
    bald: Optional[float]  # microsoft
    invisible: Optional[bool]  # microsoft

    @staticmethod
    def default() -> "FaceHair":
        return FaceHair(hair_color=[], bald=None, invisible=None)


class FaceFacialHair(NoRaiseBaseModel):
    moustache: Optional[float]  # microsoft, amazon
    beard: Optional[float]  # microsoft, amazon
    sideburns: Optional[float]  # microsoft

    @staticmethod
    def default() -> "FaceFacialHair":
        return FaceFacialHair(moustache=None, beard=None, sideburns=None)


class FaceBoundingBox(NoRaiseBaseModel):
    x_min: Optional[float]
    x_max: Optional[float]
    y_min: Optional[float]
    y_max: Optional[float]

    @staticmethod
    def default() -> "FaceBoundingBox":
        return FaceBoundingBox(
            x_min=None,
            x_max=None,
            y_min=None,
            y_max=None,
        )


class FacePoses(NoRaiseBaseModel):
    pitch: Optional[float]  # all
    roll: Optional[float]  # all
    yaw: Optional[float]  # all

    @staticmethod
    def default() -> "FacePoses":
        return FacePoses(pitch=None, roll=None, yaw=None)


class FaceQuality(NoRaiseBaseModel):
    noise: Optional[float]  # microsoft
    exposure: Optional[float]  # microsoft
    blur: Optional[float]  # microsoft
    brightness: Optional[float]  # amazon
    sharpness: Optional[float]  # amazon

    @staticmethod
    def default() -> "FaceQuality":
        return FaceQuality(
            noise=None,
            exposure=None,
            blur=None,
            brightness=None,
            sharpness=None,
        )


class FaceMakeup(NoRaiseBaseModel):
    eye_make: Optional[bool]  # microsoft
    lip_make: Optional[bool]  # microsoft

    @staticmethod
    def default() -> "FaceMakeup":
        return FaceMakeup(eye_make=None, lip_make=None)


class FaceFeatures(NoRaiseBaseModel):
    eyes_open: Optional[float]  # amazon
    smile: Optional[float]  # amazon
    mouth_open: Optional[float]  # amazon

    @staticmethod
    def default() -> "FaceFeatures":
        return FaceFeatures(eyes_open=None, smile=None, mouth_open=None)


class FaceAccessories(NoRaiseBaseModel):
    sunglasses: Optional[float]  # microsoft, amazon
    reading_glasses: Optional[float]  # microsoft
    swimming_goggles: Optional[float]  # microsoft
    face_mask: Optional[float]  # microsoft
    eyeglasses: Optional[float]  # amazon
    headwear: Optional[float]  # google, microsoft

    @staticmethod
    def default() -> "FaceAccessories":
        return FaceAccessories(
            sunglasses=None,
            reading_glasses=None,
            swimming_goggles=None,
            face_mask=None,
            eyeglasses=None,
            headwear=None,
        )


class FaceOcclusions(NoRaiseBaseModel):
    eye_occluded: Optional[bool]  # microsoft
    forehead_occluded: Optional[bool]  # microsoft
    mouth_occluded: Optional[bool]  # microsoft

    @staticmethod
    def default() -> "FaceOcclusions":
        return FaceOcclusions(
            eye_occluded=None,
            forehead_occluded=None,
            mouth_occluded=None,
        )


class FaceItem(NoRaiseBaseModel):
    confidence: float
    landmarks: FaceLandmarks
    emotions: FaceEmotions
    poses: FacePoses
    age: Optional[float]
    gender: Optional[StrictStr]
    bounding_box: FaceBoundingBox
    hair: FaceHair
    facial_hair: FaceFacialHair
    quality: FaceQuality
    makeup: FaceMakeup
    accessories: FaceAccessories
    occlusions: FaceOcclusions
    features: FaceFeatures


class FaceDetectionDataClass(NoRaiseBaseModel):
    items: Sequence[FaceItem] = Field(default_factory=list)
