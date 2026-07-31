import { useState, useEffect, useRef } from "react";
import { searchStores } from "./api";
import "./SearchBar.css";

function SearchBar({ onStoreSelect }) {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const wrapperRef = useRef(null);

    // Search when typing (with a tiny delay to not spam the backend)
    useEffect(() => {
        if (query.length === 0) {
            setResults([]);
            setShowDropdown(false);
            return;
        }
        const timer = setTimeout(async () => {
            const data = await searchStores(query);
            setResults(data.stores);
            setShowDropdown(true);
        }, 300);
        return () => clearTimeout(timer);
    }, [query]);

    // Close dropdown if clicking outside
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
                setShowDropdown(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSelect = (store) => {
        setQuery(store.store_id);
        setShowDropdown(false);
        onStoreSelect(store); // Tell App.jsx to fly to this store
    };

    return (
        <div className="search-wrapper" ref={wrapperRef}>
            <input
                type="text"
                placeholder="Search Store ID (e.g. 1, 10, 100...)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="search-input"
            />

            {showDropdown && results.length > 0 && (
                <div className="search-dropdown">
                    {results.map((store) => (
                        <div key={store.store_id} className="search-item" onClick={() => handleSelect(store)}>
                            <span className="item-id">{store.store_id}</span>
                            <span className="item-name">{store.name}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default SearchBar;