from django.contrib.auth.mixins import LoginRequiredMixin


class VendAuthMixin(LoginRequiredMixin):
    def get_queryset(self):
        retailer = self.request.user.vendprofile.retailer
        return self.model.objects.filter(retailer=retailer)


class VendAuthSingleObjectSyncMixin(VendAuthMixin):

    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_object(self):
        retailer = self.request.user.vendprofile.retailer
        uid = self.kwargs.get('uid')
        self.model.objects.synchronise(retailer, uid)
        return super(VendAuthSingleObjectSyncMixin, self).get_object()


class VendAuthCollectionSyncMixin(VendAuthMixin):
    def get_queryset(self):
        retailer = self.request.user.vendprofile.retailer
        self.model.objects.synchronise(retailer)
        return super(VendAuthCollectionSyncMixin, self).get_queryset()

