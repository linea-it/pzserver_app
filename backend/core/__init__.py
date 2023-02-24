from rest_framework.metadata import SimpleMetadata


class SimpleMetadataWithFilters(SimpleMetadata):

    def determine_metadata(self, request, view):

        metadata = super(
            SimpleMetadataWithFilters, self
        ).determine_metadata(request, view)

        if hasattr(view, 'filterset_class'):
            filters = list()
            for filter_name, filter_type in view.filterset_class.base_filters.items():
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

            metadata['filters'] = filters

        if hasattr(view, 'search_fields'):
            metadata['search'] = view.search_fields

        if hasattr(view, 'ordering_fields'):
            metadata['ordering'] = view.ordering_fields

        return metadata
