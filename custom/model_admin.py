from django.contrib import admin
from django.contrib.admin.views.main import ChangeList


class BaseChangeList(ChangeList):

    def __init__(self, request, model, list_display, list_display_links,
                 list_filter, date_hierarchy, search_fields, list_select_related,
                 list_per_page, list_max_show_all, list_editable, model_admin, other_list_filter=None):

        self.other_list_filter = other_list_filter

        super(BaseChangeList, self).__init__(request, model, list_display, list_display_links,
                                             list_filter, date_hierarchy, search_fields, list_select_related,
                                             list_per_page, list_max_show_all, list_editable, model_admin)

    def get_filters(self, request):
        (filter_specs, has_filters, lookup_params,
         use_distinct) = super().get_filters(request)

        if self.other_list_filter and lookup_params:
            for other in self.other_list_filter:
                if other in lookup_params:
                    lookup_params.pop(other)

        return filter_specs, has_filters, lookup_params, use_distinct


class BaseModelAdmin(admin.ModelAdmin):

    other_list_filter = []

    def lookup_allowed(self, lookup, value):
        if lookup in self.other_list_filter:
            return True
        return super().lookup_allowed(lookup, value)

    def get_changelist(self, request, **kwargs):
        return BaseChangeList

    def get_changelist_instance(self, request):
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        # Add the action checkboxes if any actions are available.
        if self.get_actions(request):
            list_display = ['action_checkbox'] + list(list_display)
        BaseChangeList = self.get_changelist(request)
        return BaseChangeList(
            request,
            self.model,
            list_display,
            list_display_links,
            self.get_list_filter(request),
            self.date_hierarchy,
            self.get_search_fields(request),
            self.get_list_select_related(request),
            self.list_per_page,
            self.list_max_show_all,
            self.list_editable,
            self,
            self.other_list_filter,
        )
