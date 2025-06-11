#backend/faq_api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from faq_api.models import ClusterRun
from faq_api.serializers import ClusterResultSerializer

@api_view(['GET'])
def cluster_results(request):
    run_id = request.GET.get("run_id")

    if run_id:
        try:
            run = ClusterRun.objects.get(id=run_id)
        except ClusterRun.DoesNotExist:
            return Response({"error": "Invalid run_id"}, status=404)
    else:
        run = ClusterRun.objects.order_by("-created_at").first()

    if not run:
        return Response({"clusters": [], "clusters_map": []})

    clusters = run.clusters.all().order_by("cluster_id")
    serialized = ClusterResultSerializer(clusters, many=True)

    return Response({
        "clusters": serialized.data,
        "run_id": run.id,
        "run_timestamp": run.created_at.isoformat(),
        "clusters_map": run.cluster_map or []
    })
