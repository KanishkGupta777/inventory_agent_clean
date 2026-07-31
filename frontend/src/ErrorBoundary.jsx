import { Component } from "react";

class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError() {
        return { hasError: true };
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{ padding: "20px", backgroundColor: "#fff3cd", borderRadius: "8px", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column" }}>
                    <h3 style={{ color: "#856404" }}>⚠️ Map Blocked by Network</h3>
                    <p style={{ color: "#666" }}>Organization security blocked the map tiles, but the app is still alive!</p>
                </div>
            );
        }
        return this.props.children;
    }
}

export default ErrorBoundary;