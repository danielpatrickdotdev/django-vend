from django.contrib.auth.mixins import LoginRequiredMixin


class VendAuthMixin(LoginRequiredMixin):
    def get_queryset(self):
        retailer = self.request.user.vendprofile.retailer
        return self.model.objects.filter(retailer=retailer)


class VendAuthSingleObjectSyncMixin(VendAuthMixin):
    def get_object(self):
        retailer = self.request.user.vendprofile.retailer
        pk = self.kwargs.get(self.pk_url_kwarg)
        self.model.objects.synchronise(retailer, pk)
        return super(VendAuthSingleObjectSyncMixin, self).get_object()


class VendAuthCollectionSyncMixin(VendAuthMixin):
    def get_queryset(self):
        retailer = self.request.user.vendprofile.retailer
        self.model.objects.synchronise(retailer)
        return super(VendAuthCollectionSyncMixin, self).get_queryset()

