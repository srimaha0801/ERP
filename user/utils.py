from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    # Addings role info in token
    refresh['is_staff'] = user.is_staff
    refresh['is_superuser'] = user.is_superuser

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }