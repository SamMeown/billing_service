from sqladmin import ModelAdmin

from ..db.db_models import ModelSubscriptions, ModelUsers, ModelUserSubscription, ModelMovies


class SubscriptionAdmin(ModelAdmin, model=ModelSubscriptions):
    column_list = [ModelSubscriptions.id, ModelSubscriptions.name, ModelSubscriptions.price]
    column_searchable_list = [ModelSubscriptions.name]
    column_sortable_list = [ModelSubscriptions.name, ModelSubscriptions.price]


class MovieAdmin(ModelAdmin, model=ModelMovies):
    column_list = [ModelMovies.id, ModelMovies.name, ModelMovies.price]
    column_searchable_list = [ModelMovies.name]
    column_sortable_list = [ModelMovies.name, ModelMovies.price]


class UsersAdmin(ModelAdmin, model=ModelUsers):
    pass


class UserSubscriptionAdmin(ModelAdmin, model=ModelUserSubscription):
    # column_details_list = [ModelUserSubscription.user_id, ModelUserSubscription.sub_id,
    #                        ModelUserSubscription.expired_time]
    pass
