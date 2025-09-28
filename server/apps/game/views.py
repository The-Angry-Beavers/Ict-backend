from django.http import HttpRequest
from ninja import Router


from server.apps.game.services.dto import (
    GenerateSituationParams,
    Situation,
    SituationHint,
    AcknowledgeDayFinish,
    AcknowledgeDayFinishResponse,
)
from server.apps.game.services import generation


router = Router()


@router.post("/generateSituation", response=Situation)
def generate_situation(
    request: HttpRequest, generation_params: GenerateSituationParams
) -> Situation:
    generation_instance = generation.generate_situation(generation_params)
    return Situation.from_generation_model(generation_instance)


@router.post("/getHint", response=SituationHint)
def get_hint(
    request: HttpRequest, generation_params: GenerateSituationParams
) -> SituationHint:
    hint_instance = generation.get_hint(generation_params)
    return SituationHint.model_validate(
        hint_instance,
        from_attributes=True,
    )


@router.post("/acknowledgeDayFinish", response=AcknowledgeDayFinish)
def acknowledge_day_finish(
    request: HttpRequest, data: AcknowledgeDayFinish
) -> AcknowledgeDayFinishResponse:
    return generation.acknowledge_day_finish(data)
