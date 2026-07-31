import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import ErrorBoundary from "./ErrorBoundary";
import "leaflet/dist/leaflet.css";

// Fix for Vite missing icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
    iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

function MapComponent({ stores, onPinClick }) {
    return (
        <ErrorBoundary>
            <MapContainer
                center={[26.9124, 75.7873]}
                zoom={5}
                style={{ height: "100%", width: "100%" }}
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; OpenStreetMap contributors'
                />

                {stores.map((store) => (
                    <Marker
                        key={store.store_id}
                        position={[store.lat, store.lng]}
                        eventHandlers={{ click: () => onPinClick(store) }}
                    >
                        <Popup>
                            <b>Store {store.store_id}</b><br />{store.name}
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </ErrorBoundary>
    );
}

export default MapComponent;