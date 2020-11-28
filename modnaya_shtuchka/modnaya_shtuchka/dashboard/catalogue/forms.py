from oscar.apps.dashboard.catalogue import forms as base_forms


class ProductAttributesForm(base_forms.ProductAttributesForm):
    class Meta(base_forms.ProductAttributesForm.Meta):
        fields = ["ordering", "name", "code", "type", "option_group", "required"]

