import React, { useState, useEffect } from "react";
import axios from "axios";

const baseurl = process.env.REACT_APP_BASEAPI;

const ItemsPage = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await axios.get(`${baseurl}/api/product-service-items/`);
        setItems(response.data);
      } catch (error) {
        console.error("Error fetching items:", error);
        setError("Failed to load items.");
      } finally {
        setLoading(false);
      }
    };
    fetchItems();
  }, []);

  const handleSaveItem = async (newItem) => {
    try {
      const endpoint = newItem.type === "service" ? 
        `${baseurl}/service-item/create/` : `${baseurl}/product-item/create/`;
      await axios.post(endpoint, newItem);
      setItems([...items, newItem]);
    } catch (error) {
      console.error("Error saving item:", error);
      alert("Failed to save item.");
    }
  };

  const handleDeleteItem = async (id, type) => {
    try {
      const endpoint = type === "service" ? 
        `${baseurl}/service-item/${id}/` : `${baseurl}/product-item/${id}/`;
      await axios.delete(endpoint);
      setItems(items.filter(item => item.id !== id));
    } catch (error) {
      console.error("Error deleting item:", error);
      alert("Failed to delete item.");
    }
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h1>Items</h1>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            {item.item_name || item.service_name} - {item.type}
            <button onClick={() => handleDeleteItem(item.id, item.type)}>Delete</button>
          </li>
        ))}
      </ul>
      {/* Add UI for creating new items here and call handleSaveItem */}
    </div>
  );
};

export default ItemsPage;
