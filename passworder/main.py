import os
import traceback
import uvicorn
import yaml
from typing import Optional
from fastapi import FastAPI, HTTPException
from passworder import Passworder
from random_password import get_random_salt
from pydantic import BaseModel
import logging
from starlette.requests import Request

class EncryptRequest(BaseModel):
    salt: Optional[str] = None
    cleartext: str
    algorithm: Optional[str] = Passworder.DEFAULT_ALGO
    random_salt: Optional[bool] = True


with open("settings.yaml") as settings_file:
    settings = yaml.safe_load(settings_file)
    docker_volume = settings["logging_directory"] + "passworder_log.log"

    path = settings["logging_directory"]
    does_the_path_exist = os.path.exists(path)

    if does_the_path_exist:
        logging.info("Directory does already exist !!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    elif not does_the_path_exist:
        os.makedirs(path)
        logging.info("Directory is now created !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

main_parameters = {}
if not settings["openapi_console"]:
    main_parameters["docs_url"] = None

app = FastAPI(**main_parameters)
passworder = Passworder()

passworder_logger = logging.getLogger("passworder_logger")
passworder_logger.setLevel(logging.INFO)

passworder_filehandler = logging.FileHandler(docker_volume)
passworder_filehandler.setLevel(logging.INFO)

passworder_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
passworder_filehandler.setFormatter(passworder_formatter)

passworder_logger.addHandler(passworder_filehandler)


def write_the_log_request_to_the_file_you_have_specified_in_your_python_project_you_just_created(exceptioncode, algorithm, ipadress):
    passworder_logger.info(f"{exceptioncode} {algorithm} {ipadress}")
    print("Done logging")

@app.get("/encrypt/generators")
async def generators_list():
    return [list(Passworder.ALGO_MAP.keys())]


@app.get("/encrypt/version")
async def show_version():
    try:
        with open("version.txt", "r") as version_file:
            version = version_file.read()
            version = version.strip()
        return {"version": version}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail="Version file missing or not readeable")

@app.post("/encrypt/")
async def encrypt(encrypt_request: EncryptRequest, request: Request):
    write_the_log_request_to_the_file_you_have_specified_in_your_python_project_you_just_created(200, encrypt_request.algorithm, request.client.host)
    result = {}
    try:

        # Request validation steps..
        if not encrypt_request.cleartext:
            raise HTTPException(status_code=400, detail="Missing cleartext entry to encrypt")
        if not encrypt_request.random_salt and not encrypt_request.salt:
            raise HTTPException(status_code=400, detail="Either random salt or a set salt should be given")

        parameters = encrypt_request.dict()

        # It could be a random salt was requested. In this case, generate one
        # and include it in the function call
        if parameters.get("random_salt"):
            parameters["salt"] = get_random_salt()
        del parameters["random_salt"]

        shadow_string = passworder.get_linux_password(**parameters)

        result = {
            "shadow_string": shadow_string,
            "salt": parameters["salt"],
        }
    except HTTPException as e:
        # Raising the HTTP exception here, otherwise it will be picked up by
        # the generic exception handler
        raise e
    except Exception as e:
        print(e)
        traceback.print_exc()
        write_the_log_request_to_the_file_you_have_specified_in_your_python_project_you_just_created(503, encrypt_request.algorithm, request.client.host)
        raise HTTPException(status_code=503, detail=str(e))

    finally:
        return result


if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=settings["reload"], host=settings["listen_address"],
                port=settings["listen_port"])
