from django.http import JsonResponse
import base64
import requests
from rest_framework.response import Response
from rest_framework import status



def getBilasToken(request):
    username = "SharpShopper"
    password = "sharpshopper"

    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    url = "https://bilalsadasub.com/api/user"
    headers = {"Authorization": f"Basic {encoded_credentials}"}

    res = requests.post(url, headers=headers)
    
    if res.status_code == 200:
        data = res.json()
        
        # Example: get AccessToken if present
        access_token = data.get("AccessToken")
        
        return Response({
                "status": status.HTTP_200_OK,
                'token': access_token,
                'message': 'Token generated'
            })
        
    else:
        print("Request failed:", res.status_code, res.text)
        return   Response({
                "status": status.HTTP_200_OK,
                'message': 'Token generation failed'
            })
    
        
    
    # print( "JsonResponse(res.json(), safe=False)")
    # print( JsonResponse(res.json(), safe=False))

    # # Return JSON response directly to the browser
    # return JsonResponse(res.json(), safe=False)



