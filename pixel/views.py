from django.shortcuts import render

# Create your views here.
import google.generativeai as genai
from bs4 import BeautifulSoup
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Pixel
# Configure Gemini API
GENAI_API_KEY = "AIzaSyBdDZPK-Kv7phn-BZuxVzdLEI-80Wq2Fyw"
genai.configure(api_key=GENAI_API_KEY)



def get_main_product_image(html_content, site_url):
    
    prompt = f"""
    This is a content of body of a html.
    {html_content}

    Please analyze and determine which one is the main product image.
    
    This is the site URL: {site_url}, if you do not find the full url of image, just use the site url to get the image link.
    
    If the image url is encoded, you have to decode it yourself.
    
    NOTE: Only OUTPUT THE IMAGE URL, nothing else.
    """
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    return response.text.strip() if response.text else None

def get_product_image_view(html_content, site_url):
    if not html_content:
        return Response({"error": "Missing 'html_content' in request body"}, status=status.HTTP_400_BAD_REQUEST)

    main_product_image = get_main_product_image(html_content, site_url)
    
    if not main_product_image:
        return {"message": "No main product image found"}

    return main_product_image



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def track_pixel(request):
    if request.method == "POST":
        try:
            # Print full request body to debug
            # print("Raw Request Body:", request.body.decode('utf-8'))

            # Parse JSON data
            data = json.loads(request.body)
            
            # Check if `bodyContent` is present
            if 'bodyContent' not in data:
                return JsonResponse({"error": "bodyContent missing"}, status=400)


            # Process the `bodyContent`
            image = get_product_image_view(data['bodyContent'], data['url'])

            pixel = Pixel(ip=data['ip'], time_spend= data['timeSpent'], website_url = data['url'], image_link = image)
            pixel.save()
            
            print("Processed Image:", image)

            return JsonResponse({"status": "success"})
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)