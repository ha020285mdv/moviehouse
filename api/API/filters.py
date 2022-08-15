from rest_framework import filters


class SessionsFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        hall = request.query_params.get('hall')
        start_between = request.query_params.get('time_start_range')
        if hall:
            queryset = queryset.filter(settings__hall__name=hall)
        if start_between:
            start_between = start_between.split(",")
            queryset = queryset.filter(settings__time_start__gte=start_between[0],
                                       settings__time_start__lte=start_between[1])
        return queryset
