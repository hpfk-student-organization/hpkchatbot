from aiogram import Router

from middlewares.get_name_function import GetNameFunctionMiddleware

router = Router()

router.errors.middleware(
    GetNameFunctionMiddleware()
)
