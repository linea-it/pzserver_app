from rest_framework.metadata import SimpleMetadata


class SimpleMetadataWithFilters(SimpleMetadata):

    def determine_metadata(self, request, view):
        metadata = super(
            SimpleMetadataWithFilters, self
        ).determine_metadata(request, view)

        filter_items = list()

        if hasattr(view, 'filterset_class'):  # django-filter plugin
            filter_items = view.filterset_class.base_filters.items()
        elif hasattr(view, 'filter_class'):  # drf default
            filter_items = view.filter_class.base_filters.items()

        if filter_items:
            filters = list()
            for filter_name, filter_type in filter_items:
                filter_obj = {
                    "name": filter_name,
                    "type": filter_type.__class__.__name__
                }

                choices = filter_type.extra.get('choices', False)
                if choices:
                    filter_obj['choices'] = [
                        {
                            "value": choice_value,
                            "display_name": choice_name
                        }
                        for choice_value, choice_name in choices
                    ]

                filters.append(filter_obj)

            metadata['filter_classes'] = filters

        if hasattr(view, 'filterset_fields'):
            metadata['filterset'] = view.filterset_fields

        if hasattr(view, 'search_fields'):
            metadata['search'] = view.search_fields

        if hasattr(view, 'ordering_fields'):
            metadata['ordering'] = view.ordering_fields

        return metadata
