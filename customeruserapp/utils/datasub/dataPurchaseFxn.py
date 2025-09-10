import requests
from rest_framework.response import Response
from rest_framework import status

def PurchaseData(token, network, dataPlan, dataRequestID, phone):
    print('PurchaseData')
    url = 'https://bilalsadasub.com/api/data'
        
    payload = {
        "network": network,
        "phone": phone,
        "data_plan": dataPlan,
        "bypass": False,
        "request-id": f"Data_{dataRequestID}"
    }

    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)

    try:
        data = response.json()
    except Exception as e:
        return Response(
            {"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid JSON response"},
            status=status.HTTP_502_BAD_GATEWAY
        )

    # ✅ Always return a DRF Response
    if response.status_code == 200:
        return Response({
            "status": status.HTTP_200_OK,
            "api_response": data   # <-- now you can access data['message']
        }, status=status.HTTP_200_OK)

    else:
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "api_response": data
        }, status=response.status_code)