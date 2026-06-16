from copy import deepcopy

from app.db.models import Employee
from app.db.repository import (
    create_prediction_input,
    create_prediction_output,
    find_matching_employee,
    get_employee_by_business_id,
)
from app.schemas.prediction import PREDICTION_INPUT_EXAMPLE


#********************************
#* Fabrique de donnees         *
#********************************

def build_payload(**overrides):
    payload = deepcopy(PREDICTION_INPUT_EXAMPLE)
    payload.update(overrides)
    return payload


def build_employee_payload(id_employee: int = 1001, **overrides):
    payload = build_payload(**overrides)
    payload["id_employee"] = id_employee
    return payload


#********************************
#* Tests lecture employees     *
#********************************

def test_get_employee_by_business_id_returns_employee(db_session):
    employee = Employee(**build_employee_payload(id_employee=2068))
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    result = get_employee_by_business_id(db_session, employee.id_employee)

    assert result is not None
    assert result.id_employee == employee.id_employee


def test_get_employee_by_business_id_returns_none(db_session):
    result = get_employee_by_business_id(db_session, 999999)

    assert result is None


def test_find_matching_employee_returns_employee(db_session):
    payload = build_payload()

    employee = Employee(**build_employee_payload(id_employee=2068))
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    result = find_matching_employee(db_session, payload)

    assert result is not None
    assert result.id_employee == employee.id_employee


def test_find_matching_employee_returns_none_when_no_match(db_session):
    employee = Employee(**build_employee_payload(id_employee=2068))
    db_session.add(employee)
    db_session.commit()

    result = find_matching_employee(db_session, build_payload(age=55))

    assert result is None


#********************************
#* Tests prediction_inputs      *
#********************************

def test_create_prediction_input_with_id_employee(db_session):
    employee = Employee(**build_employee_payload(id_employee=2068))
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    prediction_input = create_prediction_input(
        db_session,
        build_payload(),
        id_employee=employee.id_employee,
    )

    assert prediction_input.id is not None
    assert prediction_input.id_employee == employee.id_employee
    assert prediction_input.age == 38


def test_create_prediction_input_without_id_employee(db_session):
    prediction_input = create_prediction_input(db_session, build_payload())

    assert prediction_input.id is not None
    assert prediction_input.id_employee is None


#********************************
#* Tests prediction_outputs     *
#********************************

def test_create_prediction_output_persists_all_fields(db_session):
    prediction_input = create_prediction_input(db_session, build_payload())

    prediction_result = {
        "prediction": 1,
        "probability": 0.87,
        "threshold": 0.211717,
        "label": "risque_attrition_important",
    }

    prediction_output = create_prediction_output(
        db_session,
        prediction_input_id=prediction_input.id,
        prediction_result=prediction_result,
        model_name="final_model",
        model_version="0.1.0",
    )

    assert prediction_output.id is not None
    assert prediction_output.prediction_input_id == prediction_input.id
    assert prediction_output.prediction == 1
    assert prediction_output.probability == 0.87
    assert prediction_output.threshold == 0.211717
    assert prediction_output.label == "risque_attrition_important"
    assert prediction_output.model_name == "final_model"
    assert prediction_output.model_version == "0.1.0"
