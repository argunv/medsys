USER_CREATION_FIELDS = (
    'username', 'first_name', 'last_name', 'email', 'phone', 'user_level'
)

USER_CHANGE_FIELDS = (
    'username', 'first_name', 'last_name', 'email', 'phone', 'user_level', 'is_active'
)

USER_LIST_DISPLAY = (
    'username', 'first_name', 'last_name', 'email', 'phone', 'user_level', 'is_active'
)

USER_SEARCH_FIELDS = (
    'username', 'first_name', 'last_name', 'email', 'phone'
)

USER_LIST_FILTER = ('user_level', 'is_active')

USER_FIELDSETS = (
    (None, {'fields': ('username', 'password')}),
    ('Personal info', {
        'fields': ('first_name', 'last_name', 'email', 'phone', 'user_level'),
    }),
    ('Permissions', {'fields': ('is_active',)}),
    ('Important dates', {'fields': ('last_login', 'date_joined')}),
)

USER_ADD_FIELDSETS = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'first_name', 'last_name', 'email', 'phone', 'user_level', 'password1', 'password2'),
    }),
)
