#!/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START import_libraries]
import webapp2
import googleapiclient.discovery
import json
# [END import_libraries]

def make_api_call(uri, features, num_results=1000):
  """Run a request for the specified features on the image at the given URI"""
  ### Suggestion ###
  # The only change you might want to make to this function is automatically
  # sending a fixed list of requests, rather than having this as an argument

  # [START authenticate]
  service = googleapiclient.discovery.build('vision', 'v1')
  # [END authenticate]

  # [START construct_request]
  service_request = service.images().annotate(body={
      'requests': [{
          'image': {
              'source': {
                  'imageUri': uri
	    }
          },
          # Note that features is a list of dictionaries, each dictionary containing
          # something for 'type' (e.g. 'FACE_DETECTION') and something for maxResults
          'features': [{
              'type' : feature,
              'maxResults': num_results
          } for feature in features]
      }]
  })
  # [END construct_request]
  
  # send request!
  return service_request.execute()
    

def parse_results(response, features):
  """Given a response from the API, create pretty HTML"""
  
  # We assume that there is only one result object (ie only 1 image was requested)
  results = response['responses'][0]
  
  def pretty_string_list(my_list):
    """Adds commas and 'and' to a list, creating a human-readable string"""
    items = ''
    for i in range(len(my_list)):
      items += str(my_list[i])
      if i < len(my_list) - 2:
        items += ', '
      elif i == len(my_list) - 2:
        items += ' and '
    return items

  def annotations_to_descriptions_string(annos):
    """Gets a pretty list string of the descriptions of annotations"""
    return pretty_string_list([item['description'] for item in annos])

  def parse_face_results(annotations):
    """Returns HTML for the face API results, including the face states"""
    stem = '<b>' + str(len(annotations)) + ' face results detected:</b> '

    def get_emotion(face):
      """Gives a most-probable description string of the face's state"""
      for key in face:
        if face[key] == "VERY_LIKELY":
          return "very likely to be " + key[0:-10]
      for key in face:
        if face[key] == "LIKELY":
          return "likely to be " + key[0:-10]
      for key in face:
        if face[key] == "POSSIBLE":
          return "possibly " + key[0:-10]
      return "unknown"
    
    return stem + pretty_string_list(["one " + get_emotion(face) for face in annotations])

  def parse_label_results(annotations):
    """Returns HTML for the label API results (just lists them)"""
    return '<b>Label results detected:</b> ' + annotations_to_descriptions_string(annotations)
    
  def parse_landmark_results(annotations):
    """Returns HTML for the landmark API results (just lists them)"""
    return '<b>Landmark results detected:</b> ' + annotations_to_descriptions_string(annotations)
    
  def parse_logo_results(annotations):
    """Returns HTML for the logo API results (just lists them)"""
    return '<b>Logo results detected:</b> ' + annotations_to_descriptions_string(annotations)
    
  def parse_text_result(annotations):
    """Returns HTML for the text API results (just lists the full text)"""
    return '<b>Text results detected:</b> <blockquote>' + annotations['text'] + '</blockquote>'
    
  def parse_web_results(annotations):
    """Returns HTML for the web API results (just lists them)"""
    return '<b>Web results detected:</b> ' + annotations_to_descriptions_string(annotations['webEntities'])
    
  def parse_safe_search_results(annotation):
    """Returns HTML for the safe search API results"""
    result = '<b>Safe search results detected:</b> '
    # Gives the probability for each type of risk
    result += pretty_string_list([key + ': <i>' + " ".join(annotation[key].lower().split('_')) + '</i>' for key in annotation])
    return result

  # Used to work out which function to use to parse which result
  feature_parse_map = {
    'faceAnnotations': parse_face_results,
    'labelAnnotations': parse_label_results,
    'landmarkAnnotations': parse_landmark_results,
    'logoAnnotations': parse_logo_results,
    'fullTextAnnotation': parse_text_result,
    'webDetection': parse_web_results,
    'safeSearchAnnotation': parse_safe_search_results,
  }

  # Used to match the results to the requested information
  feature_req_map = {
    'faceAnnotations': 'FACE_DETECTION',
    'labelAnnotations': 'LABEL_DETECTION',
    'landmarkAnnotations': 'LANDMARK_DETECTION',
    'logoAnnotations': 'LOGO_DETECTION',
    'fullTextAnnotation': 'TEXT_DETECTION',
    'webDetection': 'WEB_DETECTION',
    'safeSearchAnnotation': 'SAFE_SEARCH_DETECTION',
  }

  parsed_results = []
  # Parse each result if it is in the requested list, and remove it from that list
  for annotation in results:
    if annotation in feature_req_map and feature_req_map[annotation] in features:
      parsed_results += [feature_parse_map[annotation](results[annotation])]
      features.remove(feature_req_map[annotation])
  # Include a list of the features requested but no results returned
  if len(features) > 0:
    parsed_results += ['No results for ' + pretty_string_list([" ".join(feature.lower().split('_')) for feature in features])]
  # Return final parsed string
  return parsed_results

# This class serves POST requests
class ServePage(webapp2.RequestHandler):
    def post(self):
        # Extract info from request
        uri = self.request.POST.get('uri')
        features = self.request.POST.getall('features[]')
        # Make API call
        api_result = make_api_call(uri, features)
        # Parse result from API call
        parsed_results = parse_results(api_result, features)
        # Put this result in the response
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(json.dumps({'results': parsed_results}))

# This class is not used in the final app - the main page is static
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        result = 'Test - Hello World.'
        self.response.write(result)

# Create an app including the serve class
app = webapp2.WSGIApplication([
    ('/request', ServePage),
], debug=True)
