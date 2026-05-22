from copy import deepcopy

from app.db.models import Employee
from app.db.repository import (
    create_prediction_input,
    create_prediction_output,
    find_matching_employee,
    get_employee_by_id,
)
from app.schemas.prediction import PREDICTION_INPUT_EXAMPLE


#********************************
#* Fabrique de donnees         *
#********************************

def build_payload(**overrides):
    payload = deepcopy(PREDICTION_INPUT_EXAMPLE)
    payload.update(overrides)
    return payload


#********************************
#* Tests lecture employees     *
#********************************

def test_get_employee_by_id_returns_employee(db_session):
    employee = Employee(**build_payload())
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    result = get_employee_by_id(db_session, employee.id)

    assert result is not None
    assert result.id == employee.id


def test_get_employee_by_id_returns_none(db_session):
    result = get_employee_by_id(db_session, 999999)

    assert result is None


def test_find_matching_employee_returns_employee(db_session):
    payload = build_payload()

    employee = Employee(**payload)
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    result = find_matching_employee(db_session, payload)

    assert result is not None
    assert result.id == employee.id


def test_find_matching_employee_returns_none_when_no_match(db_session):
    employee = Employee(**build_payload())
    db_session.add(employee)
    db_session.commit()

    result = find_matching_employee(db_session, build_payload(age=55))

    assert result is None


#********************************
#* Tests prediction_inputs      *
#********************************

def test_create_prediction_input_with_employee_id(db_session):
    employee = Employee(**build_payload())
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    prediction_input = create_prediction_input(
        db_session,
        build_payload(),
        employee_id=employee.id,
    )

    assert prediction_input.id is not None
    assert prediction_input.employee_id == employee.id
    assert prediction_input.age == 38


def test_create_prediction_input_without_employee_id(db_session):
    prediction_input = create_prediction_input(db_session, build_payload())

    assert prediction_input.id is not None
    assert prediction_input.employee_id is None


#********************************
#* Tests prediction_outputs     *
#********************************

def test_create_prediction_output_persists_all_fields(db_session):
    prediction_input = create_prediction_input(db_session, build_payload())

    prediction_result = {
        "prediction": 1,
        "probability": 0.87,
        "threshold": 0.211717,
        "label": "attrition",
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
    assert prediction_output.label == "attrition"
    assert prediction_output.model_name == "final_model"
    assert prediction_output.model_version == "0.1.0"
