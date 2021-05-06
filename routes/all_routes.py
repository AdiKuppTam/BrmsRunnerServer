from routes.auth_routers import SignupApi, LoginApi
from routes.app_routers import DashboardApi, UploadExperimentApi


def initialize_routes(api):
    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(LoginApi, '/api/auth/login')

    api.add_resource(DashboardApi, '/api/app/dashboard')
    api.add_resource(UploadExperimentApi, '/api/app/upload')
