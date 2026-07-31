import { useState, useEffect, useRef, useCallback } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import ErrorBoundary from "./ErrorBoundary";
import SearchBar from "./SearchBar";
import Login from "./Login";
import { getAllStores, runAgent, getAgentStatus } from "./api";
import "leaflet/dist/leaflet.css";
import "./App.css";

// Fix for Vite missing icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

function App() {
  const [user, setUser] = useState(null); // null means not logged in
  const [stores, setStores] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedStoreId, setSelectedStoreId] = useState(null);
  const mapRef = useRef(null);

  // 1. Load stores ONLY if Admin logs in
  useEffect(() => {
    if (user?.role === "admin") {
      getAllStores().then((data) => setStores(data.stores));
    }
  }, [user]);

  // 2. Auto-run AI the moment a Manager logs in (so they don't see empty text)
  useEffect(() => {
    if (user?.role === "manager" && user.store_id) {
      handleRunAgent(user.store_id, `Manager Store ${user.store_id}`);
    }
  }, [user]);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setResult(null);
    setLoading(false);
  };

  // 3. Fly to store when search result clicked (Admin only)
  const handleStoreSelect = useCallback((store) => {
    if (mapRef.current) {
      mapRef.current.flyTo([store.lat, store.lng], 12, { duration: 1.5 });
    }
  }, []);

  // 4. Run AI when pin is clicked (Admin only)
  const handlePinClick = useCallback(async (store) => {
    handleRunAgent(store.store_id, store.name);
  }, []);

  // 5. The actual AI trigger logic
  const handleRunAgent = async (storeId, storeName) => {
    setLoading(true);
    setResult(null);
    setSelectedStoreId(storeId);

    try {
      const jobData = await runAgent(storeId, storeName);
      const jobId = jobData.job_id;

      const interval = setInterval(async () => {
        const statusData = await getAgentStatus(jobId);
        if (statusData.status === "completed") {
          clearInterval(interval);
          setLoading(false);
          setResult(statusData.result);
        } else if (statusData.status === "failed") {
          clearInterval(interval);
          setLoading(false);
          setResult({ error: statusData.result?.error || "Unknown error" });
        }
      }, 5000);
    } catch (error) {
      console.error("Backend error:", error);
      setLoading(false);
    }
  };

  // --- SCREEN ROUTING ---

  // Show Login Screen if not logged in
  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  // Show Dashboard if logged in
  return (
    <div className="app-container">

      {/* TOP BAR */}
      <div className="top-bar">
        <h1>🍽️ Restaurant AI ({user.role === "admin" ? "Admin Portal" : `Manager - Store #${user.store_id}`})</h1>
        <button className="logout-btn" onClick={() => setUser(null)}>Logout</button>
      </div>

      <div className="main-content">

        {/* LEFT: MAP (Visible ONLY to Admin) */}
        {user.role === "admin" && (
          <div className="map-section">
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
              <h2>Store Map</h2>
              <SearchBar onStoreSelect={handleStoreSelect} />
            </div>
            <div className="map-wrapper">
              <ErrorBoundary>
                <MapContainer center={[26.9124, 75.7873]} zoom={5} ref={mapRef} style={{ height: "100%", width: "100%" }}>
                  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap' />
                  {stores.map((store) => (
                    <Marker key={store.store_id} position={[store.lat, store.lng]} eventHandlers={{ click: () => handlePinClick(store) }}>
                      <Popup><b>Store {store.store_id}</b><br />{store.name}</Popup>
                    </Marker>
                  ))}
                </MapContainer>
              </ErrorBoundary>
            </div>
          </div>
        )}

        {/* RIGHT: ANALYTICS (Visible to BOTH, but full width for Manager) */}
        <div className={`analytics-section ${user.role === "manager" ? "full-width" : ""}`}>
          <h3>Analytics Panel {selectedStoreId && `(Store #${selectedStoreId})`}</h3>

          {loading && <p className="loading-text">🧠 AI Agents analyzing... (Takes ~3 mins)</p>}

          {result && !loading && (
            <div className="result-card">
              {result.error ? (
                <p style={{ color: "red" }}>Error: {result.error}</p>
              ) : (
                <>
                  <h4>Executive Summary</h4>
                  <p>{result.executive_summary}</p>
                  <h4 className="red-text">🔴 Top Priority</h4>
                  <p>{result.top_priority_issue}</p>
                  <h4>Action Plan</h4>
                  <ul>{result.final_action_plan?.map((a, i) => <li key={i}>{a}</li>)}</ul>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;