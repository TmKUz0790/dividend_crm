from rest_framework import generics
from .model_sales_funnel import Lead, Varonka, VaronkaTask
from .serializers import LeadSerializer, VaronkaSerializer, VaronkaTaskSerializer

# Lead CRUD
class LeadListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

class LeadRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


# Varonka CRUD
class VaronkaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Varonka.objects.all()
    serializer_class = VaronkaSerializer

class VaronkaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Varonka.objects.all()
    serializer_class = VaronkaSerializer

# VaronkaTask list for a given Varonka
class VaronkaTaskListAPIView(generics.ListAPIView):
    serializer_class = VaronkaTaskSerializer

    def get_queryset(self):
        varonka_id = self.kwargs.get('pk')
        return VaronkaTask.objects.filter(varonka_id=varonka_id)
