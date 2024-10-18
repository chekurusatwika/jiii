import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
from geopy.distance import geodesic

# Function to get user coordinates from their address
def get_coordinates(address):
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
    headers = {"User-Agent": "HealthcareAssistant/1.0"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    return None, None

# Function to find nearby healthcare facilities (hospitals, pharmacies, blood banks, scan centers, dialysis centers)
def find_nearby_places(lat, lon, place_type, radius=5000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="{place_type}"](around:{radius},{lat},{lon});
      way["amenity"="{place_type}"](around:{radius},{lat},{lon});
      relation["amenity"="{place_type}"](around:{radius},{lat},{lon});
    );
    out center;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json() 
    return data['elements']

# Function to generate Google Maps direction link
def generate_google_maps_link(lat_origin, lon_origin, lat_destination, lon_destination):
    return f"https://www.google.com/maps/dir/?api=1&origin={lat_origin},{lon_origin}&destination={lat_destination},{lon_destination}"

# Streamlit Interface
st.set_page_config(page_title="Nearby Healthcare Facilities", layout="wide")
st.title("Nearby Healthcare Facilities")

# User inputs for location and search radius
address = st.text_input("Enter your location:")
search_radius = st.slider("Search radius for nearby facilities (km)", 1, 20, 5) * 1000  # Convert to meters

# Find nearby healthcare facilities
if st.button("Find Nearby Facilities"):
    if address:
        with st.spinner("Finding nearby facilities..."):
            # Step 1: Get user coordinates and find nearby facilities
            lat, lon = get_coordinates(address)
            if lat and lon:
                hospitals = find_nearby_places(lat, lon, "hospital", search_radius)
                pharmacies = find_nearby_places(lat, lon, "pharmacy", search_radius)
                blood_banks = find_nearby_places(lat, lon, "blood_bank", search_radius)
                scan_centers = find_nearby_places(lat, lon, "diagnostic_center", search_radius)
                dialysis_centers = find_nearby_places(lat, lon, "dialysis", search_radius)

                # Display map
                st.subheader("Nearby Healthcare Facilities")
                m = folium.Map(location=[lat, lon], zoom_start=13)
                folium.Marker([lat, lon], popup="Your Location", icon=folium.Icon(color='red')).add_to(m)

                # Add hospitals, pharmacies, blood banks, scan centers, and dialysis centers to the map
                for hospital in hospitals:
                    if 'lat' in hospital:
                        folium.Marker([hospital['lat'], hospital['lon']], popup=hospital.get('tags', {}).get('name', 'Hospital'),
                                      icon=folium.Icon(color='blue', icon='plus-sign')).add_to(m)
                for pharmacy in pharmacies:
                    if 'lat' in pharmacy:
                        folium.Marker([pharmacy['lat'], pharmacy['lon']], popup=pharmacy.get('tags', {}).get('name', 'Pharmacy'),
                                      icon=folium.Icon(color='green', icon='medkit')).add_to(m)
                for blood_bank in blood_banks:
                    if 'lat' in blood_bank:
                        folium.Marker([blood_bank['lat'], blood_bank['lon']], popup=blood_bank.get('tags', {}).get('name', 'Blood Bank'),
                                      icon=folium.Icon(color='darkred', icon='tint')).add_to(m)
                for scan in scan_centers:
                    if 'lat' in scan:
                        folium.Marker([scan['lat'], scan['lon']], popup=scan.get('tags', {}).get('name', 'Scan Center'),
                                      icon=folium.Icon(color='purple', icon='stethoscope')).add_to(m)
                for dialysis in dialysis_centers:
                    if 'lat' in dialysis:
                        folium.Marker([dialysis['lat'], dialysis['lon']], popup=dialysis.get('tags', {}).get('name', 'Dialysis Center'),
                                      icon=folium.Icon(color='orange', icon='heart')).add_to(m)

                # Render the map
                folium_static(m)

                # Show nearby facilities with Google Maps links
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Nearby Hospitals:")
                    for hospital in hospitals[:5]:  # Limit to top 5 results
                        if 'tags' in hospital and 'name' in hospital['tags']:
                            distance = geodesic((lat, lon), (hospital['lat'], hospital['lon'])).km
                            st.write(f"{hospital['tags']['name']} - {distance:.2f} km")
                            google_maps_link = generate_google_maps_link(lat, lon, hospital['lat'], hospital['lon'])
                            st.markdown(f"[Get Directions in Google Maps]({google_maps_link})", unsafe_allow_html=True)

                    st.subheader("Nearby Blood Banks:")
                    for blood_bank in blood_banks[:5]:
                        if 'tags' in blood_bank and 'name' in blood_bank['tags']:
                            distance = geodesic((lat, lon), (blood_bank['lat'], blood_bank['lon'])).km
                            st.write(f"{blood_bank['tags']['name']} - {distance:.2f} km")
                            google_maps_link = generate_google_maps_link(lat, lon, blood_bank['lat'], blood_bank['lon'])
                            st.markdown(f"[Get Directions in Google Maps]({google_maps_link})", unsafe_allow_html=True)

                with col2:
                    st.subheader("Nearby Pharmacies:")
                    for pharmacy in pharmacies[:5]:
                        if 'tags' in pharmacy and 'name' in pharmacy['tags']:
                            distance = geodesic((lat, lon), (pharmacy['lat'], pharmacy['lon'])).km
                            st.write(f"{pharmacy['tags']['name']} - {distance:.2f} km")
                            google_maps_link = generate_google_maps_link(lat, lon, pharmacy['lat'], pharmacy['lon'])
                            st.markdown(f"[Get Directions in Google Maps]({google_maps_link})", unsafe_allow_html=True)

                    st.subheader("Nearby Scan and Dialysis Centers:")
                    for scan in scan_centers[:5]:
                        if 'tags' in scan and 'name' in scan['tags']:
                            distance = geodesic((lat, lon), (scan['lat'], scan['lon'])).km
                            st.write(f"{scan['tags']['name']} - {distance:.2f} km")
                            google_maps_link = generate_google_maps_link(lat, lon, scan['lat'], scan['lon'])
                            st.markdown(f"[Get Directions in Google Maps]({google_maps_link})", unsafe_allow_html=True)

                    for dialysis in dialysis_centers[:5]:
                        if 'tags' in dialysis and 'name' in dialysis['tags']:
                            distance = geodesic((lat, lon), (dialysis['lat'], dialysis['lon'])).km
                            st.write(f"{dialysis['tags']['name']} - {distance:.2f} km")
                            google_maps_link = generate_google_maps_link(lat, lon, dialysis['lat'], dialysis['lon'])
                            st.markdown(f"[Get Directions in Google Maps]({google_maps_link})", unsafe_allow_html=True)
            else:
                st.error("Unable to find coordinates for the given address.")
    else:
        st.warning("Please enter your location.")

# Sidebar instructions
st.sidebar.markdown("""
## How to use:
1. Enter your location in the input field.
2. Adjust the search radius for nearby facilities using the slider.
3. Click "Find Nearby Facilities" to get:
   - A map of nearby hospitals, pharmacies, blood banks, scan centers, and dialysis centers.
   - Links to Google Maps for directions to healthcare facilities.
""")