import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom"; // existing import (not removed)
import { Info, Layout, LayoutGrid, Barcode, Search } from "lucide-react";
// NEW: Import jsPDF and autoTable for PDF generation
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import axios from "axios";

const baseurl=process.env.REACT_APP_BASEAPI;
const MeasuringUnits=[
  "UNT", "UGS", "KGS", "LTR", "AAN", "ACS", "AC", "AMP", "BAG", "BAL", "BALL",
  "BAR", "BOU", "BLISTER", "BOLUS", "BK", "BOR", "BTL", "BOX", "BRASS", "BRICK",
  "BCK", "BKL", "BUN", "BDL", "CAN", "CAP", "CPS", "CT", "CTS", "CARD", "CTN",
  "CASE", "CMS", "CNT", "CHAIN", "CHOKA", "CHUDI", "CLT", "COIL", "CONT", "COPY",
  "COURSE", "CRT", "CRM", "CCM", "CUFT", "CFM", "CFT", "CBM", "CUP", "CV", "DAILY",
  "DANGLER", "DAY", "DEZ", "DOZ", "DROP", "DRM", "EA", "EACH", "FT", "FT2", "FIT",
  "FLD", "FREE", "FTS", "GEL", "GLS", "GMS", "GGR", "GRS", "GYD", "HF", "HEGAR",
  "HA", "HMT", "HRS", "INJECTION", "IN", "ITEM ID", "JAR", "JL", "JO", "JHL", "JOB",
  "KT", "KGS", "KLR", "KME", "KMS", "KVA", "KW", "KIT", "LAD", "LENG", "LBS", "LTR",
  "LOT", "LS", "MAN-DAY", "MRK", "MBPS", "MTR", "MMBTU", "MTON", "MG", "M/C", "MLG",
  "MLT", "MM", "MINS", "MONTH", "MON", "MORA", "NIGHT", "NONE", "NOS", "OINT", "OTH",
  "OR", "PKG", "PKT", "PAC", "PAD", "PADS", "PAGE", "PAIR", "PRS", "PATTA", "PAX",
  "PER", "PWP", "PERSON", "PET", "PHILE", "PCS", "PLT", "PT", "PRT", "POCH", "QUAD",
  "QTY", "QTL", "RTI", "REAM", "REEL", "RIM", "ROL", "ROOM", "RFT", "RMT", "RS",
  "SAC", "SEC", "SEM", "SSN", "SET", "SHEET", "SKINS", "SLEVES", "SPRAY", "SQCM",
  "SQF", "SQY", "SARAM", "STICKER", "STONE", "STRP", "SYRP", "TBS", "TGM", "TKT",
  "TIN", "TON", "TRY", "TRIP", "TRK", "TUB", "UNT", "UGS", "VIAL", "W", "WEEK",
  "YDS", "YRS"
]


// ------------------------------------------------
// UPDATED: Implement Excel download using CSV and PDF
// ------------------------------------------------
const handleDownloadExcel = (reportData) => {
  console.log("Download Excel clicked!", reportData);
  if (!reportData || !reportData.length) {
    alert("No data to download.");
    return;
  }

  // Convert reportData to CSV string
  const headers = ["Name", "Code", "MRP", "Selling Price"];
  const csvRows = [headers.join(",")];

  reportData.forEach((item) => {
    const name = item.type === "Product" ? item.item_name || "" : item.service_name || "";
    const code = item.type === "Product" ? item.item_code || "-" : item.service_code || "SRV";
    const mrp = item.mrp || "-";
    const sellingPrice = item.sales_price_with_tax || item.sales_price_without_tax || "0.00";

    csvRows.push([name, code, mrp, sellingPrice].join(","));
  });

  const csvString = csvRows.join("\n");
  const blob = new Blob([csvString], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "report.csv";
  a.click();
  window.URL.revokeObjectURL(url);
};

const handleDownloadPDF = (reportData) => {
  console.log("Download PDF clicked!", reportData);
  if (!reportData || !reportData.length) {
    alert("No data to download.");
    return;
  }

  const doc = new jsPDF("p", "pt", "a4");

  doc.setFontSize(12);
  doc.text("Business Name", 40, 40);
  doc.text("Phone no: 7010738782", 40, 60);

  doc.setFontSize(14);
  doc.text("Rate List", 400, 40);

  doc.setFontSize(10);
  const currentDate = new Date().toLocaleDateString();
  doc.text(`Date: ${currentDate}`, 400, 60);
  doc.text(`Total Items: ${reportData.length}`, 40, 80);

  // Table Headers
  const headers = [["Name", "Code", "MRP", "Selling Price"]];
  const body = reportData.map((item) => {
    const name = item.type === "Product" ? item.item_name || "" : item.service_name || "";
    const code = item.type === "Product" ? item.item_code || "-" : item.service_code || "SRV";
    const mrp = item.mrp || "-";
    const sellingPrice = item.sales_price_with_tax || item.sales_price_without_tax || "0.00";
    return [name, code, mrp, sellingPrice];
  });

  autoTable(doc, {
    startY: 100,
    head: headers,
    body: body,
    theme: "grid",
    headStyles: { fillColor: [220, 220, 220], textColor: 0 },
    margin: { left: 40, right: 40 },
  });

  doc.save("report.pdf");
};

const ItemsPage = () => {
  const [items, setItems] = useState(() => {
    return JSON.parse(localStorage.getItem("items")) || [];
  });

  const [listItems, setListItems] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  const [categories, setCategories] = useState(() => {
    const stored = JSON.parse(localStorage.getItem("itemCategories")) || [];
    let finalCats = stored.map((c) =>
      typeof c === "string" ? { name: c, isPlaceholder: false } : c
    );
    if (!finalCats.some((cat) => cat.isPlaceholder)) {
      finalCats = [{ name: "Select Category", isPlaceholder: true }, ...finalCats];
    }
    return finalCats;
  });

  useEffect(() => {
    const withoutPlaceholder = categories.filter((c) => !c.isPlaceholder);
    localStorage.setItem("itemCategories", JSON.stringify(withoutPlaceholder));
  }, [categories]);

  const updateCategories = (newCats) => {
    setCategories(newCats);
  };

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await axios.get(`${baseurl}/item/api/product-service-items/`);
        const products = response.data.products || [];
        const services = response.data.services || [];
        setListItems([...products, ...services]);
      } catch (error) {
        console.error("Error fetching items:", error);
        setListItems([]);
      }
    };
    fetchItems();
  }, []);

  const handleRowClick1 = (index) => {
    console.log("Row clicked:", listItems[index]);
  };

  const [editingCategoryIndex, setEditingCategoryIndex] = useState(null);
  const [editCategoryName, setEditCategoryName] = useState("");

  const handleEditCategory = (index) => {
    setEditingCategoryIndex(index);
    setEditCategoryName(categories[index].name);
    setSearchCatDropdownOpen(false);
    setCreateItemCatDropdownOpen(false);
  };

  const handleUpdateCategory = () => {
    if (editingCategoryIndex !== null && editCategoryName.trim()) {
      const updated = [...categories];
      updated[editingCategoryIndex] = {
        name: editCategoryName,
        isPlaceholder: false,
      };
      updateCategories(updated);
      setEditingCategoryIndex(null);
      setEditCategoryName("");
    }
  };

  const [searchCatDropdownOpen, setSearchCatDropdownOpen] = useState(false);
  const [searchSelectedCategory, setSearchSelectedCategory] = useState("Select Category");

  const handleToggleSearchCatDropdown = () => {
    setSearchCatDropdownOpen(!searchCatDropdownOpen);
  };

  const handleSelectSearchCategory = (catName) => {
    setSearchSelectedCategory(catName);
    setSearchCatDropdownOpen(false);
  };

  const [showAddCatModalGlobal, setShowAddCatModalGlobal] = useState(false);
  const [newCatNameGlobal, setNewCatNameGlobal] = useState("");

  const handleOpenAddCatModalGlobal = () => {
    setShowAddCatModalGlobal(true);
    setNewCatNameGlobal("");
    setSearchCatDropdownOpen(false);
  };

  const handleCloseAddCatModalGlobal = () => {
    setShowAddCatModalGlobal(false);
    setNewCatNameGlobal("");
  };

  const handleSaveNewCatGlobal = () => {
    if (newCatNameGlobal.trim()) {
      const newCat = { name: newCatNameGlobal };
      const updated = [...categories, newCat];
      updateCategories(updated);
      setSearchSelectedCategory(newCatNameGlobal);
      setNewCatNameGlobal("");
      setShowAddCatModalGlobal(false);
    }
  };
};
  // ------------------------------------------------
// 5) Create Item Modal
// ------------------------------------------------
const [showCreateItemModal, setShowCreateItemModal] = useState(false);
// For Product => 0=Basic,1=Stock,2=Pricing,3=PartyWise,4=Custom
// For Service => 0=Basic,1=Other,2=PartyWise,3=Custom
const [activeTab, setActiveTab] = useState(0);
const [itemType, setItemType] = useState("Product");

// Category dropdown inside Create Item
const [createItemCatDropdownOpen, setCreateItemCatDropdownOpen] = useState(false);
const [itemCat, setItemCat] = useState("Select Category");

// Basic details: Product vs. Service
const [itemName, setItemName] = useState(""); // Maps to `item_name`
const [openingStock, setOpeningStock] = useState(""); // Maps to `opening_stock`
const [serviceName, setServiceName] = useState(""); // Maps to `service_name`
const [serviceCode, setServiceCode] = useState(""); // Maps to `service_code`

// Shared price fields
const [showOnline, setShowOnline] = useState(false);
const [salesPrice, setSalesPrice] = useState(""); // Maps to `sales_price_with_tax` or `sales_price_without_tax`
const [withTax, setWithTax] = useState(true);
const [gstTaxRate, setGstTaxRate] = useState("1"); // Maps to `gst_tax_rate`
const [measuringUnit, setMeasuringUnit] = useState(""); // Maps to `measuring_unit`
const [withoutTax, setWithoutTax] = useState(true);

// Product => Stock
const [itemCode, setItemCode] = useState(""); // Maps to `product_code`
const [hsnCode, setHsnCode] = useState(""); // Maps to `hsn_code`
const [enableLowStockWarning, setEnableLowStockWarning] = useState(false); // Maps to `low_stock_warning`
const [asOfDate, setAsOfDate] = useState(""); // Maps to `as_of_date`
const [stockDescription, setStockDescription] = useState(""); // Maps to `description`
const [stockFile, setStockFile] = useState(null);

// Product => Pricing
const [purchasePrice, setPurchasePrice] = useState(""); // Maps to `purchase_price`
const [purchaseWithTax, setPurchaseWithTax] = useState(true);

// Service => Other
const [sacCode, setSacCode] = useState(""); // Maps to `sac_code`
const [description, setDescription] = useState(""); // Maps to `description`

// Nested “Add Category” modal inside Create Item
const [showAddCatModalInCreateItem, setShowAddCatModalInCreateItem] = useState(false);
const [newCatNameCreateItem, setNewCatNameCreateItem] = useState("");

const handleOpenAddCatModalInCreateItem = () => {
  setShowAddCatModalInCreateItem(true);
  setNewCatNameCreateItem("");
  setCreateItemCatDropdownOpen(false);
};

const handleCloseAddCatModalInCreateItem = () => {
  setShowAddCatModalInCreateItem(false);
  setNewCatNameCreateItem("");
};

const handleSaveNewCatInCreateItem = () => {
  if (newCatNameCreateItem.trim()) {
    const newCat = { name: newCatNameCreateItem };
    const updated = [...categories, newCat];
    updateCategories(updated);
    setItemCat(newCatNameCreateItem);
    setNewCatNameCreateItem("");
    setShowAddCatModalInCreateItem(false);
  }
};

  // ------------------------------------------------
  // NEW CODE HERE (EDITING STATES)
  // ------------------------------------------------
  const [isEditing, setIsEditing] = useState(false);
  const [editItemIndex, setEditItemIndex] = useState(null);
  
  const handleOpenCreateItem = () => {
    setShowCreateItemModal(true);
    setActiveTab(0);
    setItemType("Product");
    setItemCat("Select Category");
    setItemName(""); // Maps to `item_name`
    setOpeningStock(""); // Maps to `opening_stock`
    setServiceName(""); // Maps to `service_name`
    setServiceCode(""); // Maps to `service_code`
    setShowOnline(false);
    setSalesPrice(""); // Maps to `sales_price_with_tax` or `sales_price_without_tax`
    setWithTax(true);
    setGstTaxRate("None"); // Maps to `gst_tax_rate`
    setMeasuringUnit("Pieces(PCS)"); // Maps to `measuring_unit`
    setItemCode(""); // Maps to `product_code`
    setHsnCode(""); // Maps to `hsn_code`
    setEnableLowStockWarning(false); // Maps to `low_stock_warning`
    setAsOfDate(""); // Maps to `as_of_date`
    setStockDescription(""); // Maps to `description`
    setStockFile(null);
    setPurchasePrice(""); // Maps to `purchase_price`
    setPurchaseWithTax(true);
    setSacCode(""); // Maps to `sac_code`
    setDescription(""); // Maps to `description`
    setIsEditing(false);
    setEditItemIndex(null);
  };
  
  const handleCloseCreateItem = () => {
    setShowCreateItemModal(false);
    setIsEditing(false);
    setEditItemIndex(null);
  };
  
  const handleEditItem = (index) => {
    setIsEditing(true);
    setEditItemIndex(index);
    const itemToEdit = items[index];
  
    setItemType(itemToEdit.type || "Product");
    setItemCat(itemToEdit.category || "Select Category");
    setShowOnline(itemToEdit.showOnline || false);
    setSalesPrice(itemToEdit.sales_price_with_tax || itemToEdit.sales_price_without_tax || "");
    setWithTax(itemToEdit.sales_price_with_tax !== null);
    setGstTaxRate(itemToEdit.gst_tax_rate || "None");
    setMeasuringUnit(itemToEdit.measuring_unit || "Pieces(PCS)");
  
    if (itemToEdit.type === "product") {
      setItemName(itemToEdit.item_name || ""); // Maps correctly
      setOpeningStock(itemToEdit.opening_stock || ""); // Maps correctly
      setItemCode(itemToEdit.product_code || ""); // Maps correctly
      setHsnCode(itemToEdit.hsn_code || ""); // Maps correctly
      setEnableLowStockWarning(itemToEdit.low_stock_warning || false); // Maps correctly
      setAsOfDate(itemToEdit.as_of_date || ""); // Maps correctly
      setStockDescription(itemToEdit.description || ""); // Maps correctly
      setStockFile(null); // File handling unchanged
      setPurchasePrice(itemToEdit.purchase_price || ""); // Maps correctly
      setPurchaseWithTax(true);
    } else {
      setServiceName(itemToEdit.service_name || ""); // Maps correctly
      setServiceCode(itemToEdit.service_code || ""); // Maps correctly
      setSacCode(itemToEdit.sac_code || ""); // Maps correctly
      setDescription(itemToEdit.description || ""); // Maps correctly
    }
  
    closeDetailView();
    setShowCreateItemModal(true);
    setActiveTab(0);
  };          
 const handleSaveItem = async () => {
    const finalCat = typeof itemCat === "object" ? itemCat.name : itemCat;
  
    // Determine whether the item has "Sales Price Without Tax" or "Sales Price With Tax"
    const salesPriceWithTax = withTax ? salesPrice : null;
    const salesPriceWithoutTax = !withTax ? salesPrice : null;
  
    const newObj = {
      type: itemType,
      category: finalCat,
      item_name: itemType === "Product" ? itemName : "",
      opening_stock: itemType === "Product" ? openingStock : "",
      service_name: itemType === "Service" ? serviceName : "",
      service_code: itemType === "Service" ? serviceCode : "",
      showOnline,
      gst_tax_rate: gstTaxRate,
      measuring_unit: measuringUnit,
      product_code: itemType === "Product" ? itemCode : "",
      hsn_code: itemType === "Product" ? hsnCode : "",
      low_stock_warning: itemType === "Product" ? enableLowStockWarning : false,
      as_of_date: itemType === "Product" ? asOfDate : "",
      description: itemType === "Product" ? stockDescription : description,
      stockFile: itemType === "Product" ? stockFile : null,
      purchase_price: itemType === "Product" ? purchasePrice : "",
      purchaseWithTax: itemType === "Product" ? purchaseWithTax : false,
      sac_code: itemType === "Service" ? sacCode : "",
      sales_price_with_tax: salesPriceWithTax,
      sales_price_without_tax: salesPriceWithoutTax,
    };
  
    try {
      let response;
      if (isEditing && editItemIndex !== null) {
        // **UPDATE (PUT)**
        const editItem = items[editItemIndex];
        const itemId = editItem.id; // Ensure ID exists
  
        if (itemType === "Service") {
          response = await axios.put(`${baseurl}/item/service-item/${itemId}/`, newObj);
        } else {
          response = await axios.put(`${baseurl}/item/product-item/${itemId}/`, newObj);
        }
        console.log("Item updated successfully", response.data);
      } else {
        // **CREATE (POST)**
        if (itemType === "Service") {
          response = await axios.post(`${baseurl}/item/service-item/create/`, newObj);
        } else {
          response = await axios.post(`${baseurl}/item/product-item/create/`, newObj);
        }
        console.log("Item created successfully", response.data);
      }
  
      // Update frontend list
      if (isEditing && editItemIndex !== null) {
        const updated = [...items];
        updated[editItemIndex] = newObj;
        setItems(updated);
        localStorage.setItem("items", JSON.stringify(updated));
      } else {
        const updated = [...items, newObj];
        setItems(updated);
        localStorage.setItem("items", JSON.stringify(updated));
      }
    } catch (error) {
      console.error("Error saving item", error);
      alert("There was an error saving the item. Please try again.");
    }
  
    handleCloseCreateItem();
  };
  
  const handleConfirmDelete = async () => {
    if (deleteIndex !== null) {
      const itemToDelete = items[deleteIndex];
      const itemId = itemToDelete.id;
  
      try {
        if (itemToDelete.type === "Product") {
          await axios.delete(`${baseurl}/item/product-item/${itemId}/`);
        } else {
          await axios.delete(`${baseurl}/item/service-item/${itemId}/`);
        }
  
        console.log("Item deleted successfully");
  
        // Remove from frontend list
        const updated = items.filter((_, index) => index !== deleteIndex);
        setItems(updated);
        localStorage.setItem("items", JSON.stringify(updated));
      } catch (error) {
        console.error("Error deleting item", error);
        alert("There was an error deleting the item. Please try again.");
      }
    }
  
    setShowDeleteConfirmation(false);
    setDeleteIndex(null);
    closeDetailView();
  };
 //_______________________________________________________________________________________________________________________ 
  // ------------------------------------------------
  // Left column => tabs for Create Item Modal
  // ------------------------------------------------
  const renderLeftColumn = () => {
    const baseButtonClasses =
      "w-full text-left py-2 px-4 rounded-lg transition-colors duration-200";
    const activeButtonClasses = "bg-[#7B68EE] text-white";
    const inactiveButtonClasses = "bg-gray-100 text-gray-600 hover:bg-gray-200";
  
    if (itemType === "Product") {
      return (
        <div className="bg-white p-4 rounded-lg shadow space-y-3">
          <button
            className={`${baseButtonClasses} ${
              activeTab === 0 ? activeButtonClasses : inactiveButtonClasses
            }`}
            onClick={() => setActiveTab(0)}
          >
            Basic Details
          </button>
          <div className="text-xs text-gray-400 px-4">* Advance Details</div>
          <button
            className={`${baseButtonClasses} ${
              activeTab === 1 ? activeButtonClasses : inactiveButtonClasses
            }`}
            onClick={() => setActiveTab(1)}
          >
            Stock Details
          </button>
          <button
            className={`${baseButtonClasses} ${
              activeTab === 2 ? activeButtonClasses : inactiveButtonClasses
            }`}
            onClick={() => setActiveTab(2)}
          >
            Pricing Details
          </button>
          <button
            className={`${baseButtonClasses} ${
              activeTab === 3 ? activeButtonClasses : inactiveButtonClasses
            }`}
            onClick={() => setActiveTab(3)}
          >
            Custom Fields
          </button>
        </div>
      );
    } else {
      return (
        <div className="bg-white p-4 rounded-lg shadow space-y-3">
          <button
            className={`${baseButtonClasses} ${
              activeTab === 0 ? activeButtonClasses : inactiveButtonClasses
            }`}
            onClick={() => setActiveTab(0)}
          >
            Basic Details
          </button>
          <div className="text-xs text-gray-400 px-4">* Advance Details</div>
          <button
            className={`${baseButtonClasses} ${
              activeTab === 1 ? activeButtonClasses : inactiveButtonClasses
            }`}
            onClick={() => setActiveTab(1)}
          >
            Other Details
          </button>
          <button
            className={`${baseButtonClasses} ${
              activeTab === 2 ? activeButtonClasses : inactiveButtonClasses
            }`}
            onClick={() => setActiveTab(2)}
          >
            Custom Fields
          </button>
        </div>
      );
    }
  };
  //-_____________________________________________________________________________________________________________
  // ------------------------------------------------
  // Right column => content for Create Item Modal
  // ------------------------------------------------
  const renderBasicDetailsForProduct = () => {
    return (
      <div className="space-y-6">
        {/* Row 1: Item Type & Category */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Item Type *</label>
            <div className="flex space-x-4">
              <label className="flex items-center text-sm">
                <input
                  type="radio"
                  name="itemType"
                  value="Product"
                  checked={itemType === "Product"}
                  onChange={() => {
                    setItemType("Product");
                    setActiveTab(0);
                  }}
                  className="mr-1"
                />
                Product
              </label>
              <label className="flex items-center text-sm">
                <input
                  type="radio"
                  name="itemType"
                  value="Service"
                  checked={itemType === "Service"}
                  onChange={() => {
                    setItemType("Service");
                    setActiveTab(0);
                  }}
                  className="mr-1"
                />
                Service
              </label>
            </div>
          </div>
          <div className="relative">
            <label className="block text-sm font-medium mb-1">Category</label>
            <button
              className="w-full border rounded p-2 text-left text-sm"
              onClick={() => setCreateItemCatDropdownOpen(!createItemCatDropdownOpen)}
            >
              {typeof itemCat === "object" ? itemCat.name : itemCat}
            </button>
            {createItemCatDropdownOpen && (
              <ul className="absolute z-10 mt-1 w-full bg-white border rounded shadow">
                {categories.map((cat, idx) => (
                  <li
                    key={idx}
                    className="p-2 text-sm cursor-pointer hover:bg-gray-100"
                    onClick={() => {
                      setItemCat(cat);
                      setCreateItemCatDropdownOpen(false);
                    }}
                  >
                    {cat.name}
                  </li>
                ))}
                <li
                  className="p-2 text-sm cursor-pointer font-semibold text-[#7B68EE] hover:bg-gray-100"
                  onClick={handleOpenAddCatModalInCreateItem}
                >
                  + Add Category
                </li>
              </ul>
            )}
          </div>
        </div>
        {/* Row 2: Item Name & Show Online */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Item Name *</label>
            <input
              type="text"
              placeholder="ex: Maggie 20gm"
              value={itemName}
              onChange={(e) => setItemName(e.target.value)}
              className="w-full border rounded p-2 text-sm"
            />
            {!itemName.trim() && (
              <span className="text-xs text-red-500">Please enter the item name</span>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              Show Item in Online Store
            </label>
            <div className="flex items-center h-10">
              <input
                type="checkbox"
                checked={showOnline}
                onChange={(e) => setShowOnline(e.target.checked)}
                className="h-4 w-4"
              />
              <span className="ml-2 text-sm">Enable</span>
            </div>
          </div>
        </div>
        {/* Row 2.5: Opening Stock */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Opening Stock</label>
            <input
              type="number"
              placeholder="Enter opening stock"
              value={openingStock}
              onChange={(e) => setOpeningStock(e.target.value)}
              className="w-full border rounded p-2 text-sm"
            />
          </div>
        </div>
        {/* Measuring Unit Dropdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Measuring Unit</label>
            <select
              value={measuringUnit}
              onChange={(e) => setMeasuringUnit(e.target.value)}
              className="w-full border rounded p-2 text-sm"
            >
              {MeasuringUnits?.map((unit, index) => (
                <option key={index} value={unit}>{unit}</option>
              ))}
            </select>
          </div>
        </div>
        {/* Row 3: Sales Price */}
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Sales Price *</label>
            <div className="flex border rounded">
              <span className="flex items-center px-2 text-sm">₹</span>
              <input
                type="number"
                placeholder="200"
                value={salesPrice}
                onChange={(e) => setSalesPrice(e.target.value)}
                className="w-full p-2 text-sm focus:outline-none"
              />
            </div>
          </div>
        </div>
        {/* Tax Selection */}
        <div className="flex space-x-4 mt-1 text-sm">
          <label className="flex items-center">
            <input
              type="radio"
              checked={withTax}
              onChange={() => setWithTax(true)}
              className="mr-1"
            />
            With Tax
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              checked={!withTax}
              onChange={() => setWithTax(false)}
              className="mr-1"
            />
            No Tax
          </label>
        </div>
        {/* GST Tax Rate Dropdown */}
        <div>
          <label className="block text-sm font-medium mb-1">GST Tax Rate (%)</label>
          <select
            value={gstTaxRate}
            onChange={(e) => setGstTaxRate(e.target.value)}
            className="w-full border rounded p-2 text-sm"
          >
            <option value="0">None</option>
            <option value="5">5%</option>
            <option value="12">12%</option>
            <option value="18">18%</option>
            <option value="28">28%</option>
          </select>
        </div>
      </div>
    );
  };
  //___________________________________________________________________________________________________________________

  const autoGenerateItemCode = () => {
    const randomCode = `ITM${Math.floor(10000 + Math.random() * 90000)}`;
    setItemCode(randomCode);
  };
  
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const allowedTypes = ["image/png", "image/jpeg"];
      if (!allowedTypes.includes(file.type)) {
        alert("Only PNG and JPEG formats are allowed.");
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        alert("File size must be less than 5MB.");
        return;
      }
      setStockFile(file);
    }
  };
  
  const renderStockDetailsForProduct = () => {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Item Code with Auto-Generate Button */}
          <div className="relative">
            <label className="block text-sm font-medium mb-1">Item Code</label>
            <input
              type="text"
              placeholder="ex: ITM12549"
              value={itemCode}
              onChange={(e) => setItemCode(e.target.value)}
              className="w-full border rounded p-2 text-sm"
            />
            <button
              onClick={autoGenerateItemCode}
              className="absolute right-2 bottom-2 border rounded px-2 py-1 text-xs flex items-center space-x-1 hover:bg-gray-100"
            >
              <Barcode size={14} />
              <span>Generate</span>
            </button>
          </div>
          {/* HSN Code Input */}
          <div>
            <label className="block text-sm font-medium mb-1">HSN Code</label>
            <input
              type="text"
              placeholder="ex: 4010"
              value={hsnCode}
              onChange={(e) => setHsnCode(e.target.value)}
              className="w-full border rounded p-2 text-sm"
            />
          </div>
        </div>
  
        {/* As of Date & Low Stock Warning */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">As of Date</label>
            <input
              type="date"
              value={asOfDate}
              onChange={(e) => setAsOfDate(e.target.value)}
              className="w-full border rounded p-2 text-sm"
            />
          </div>
          <div className="flex items-center">
            <label className="block text-sm font-medium mb-1 mr-2">
              Low Stock Warning
            </label>
            <input
              type="checkbox"
              checked={enableLowStockWarning}
              onChange={(e) => setEnableLowStockWarning(e.target.checked)}
              className="h-4 w-4"
            />
          </div>
        </div>
  
        {/* Description */}
        <div>
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea
            placeholder="Enter Description"
            rows={3}
            value={description}  // Changed from stockDescription
            onChange={(e) => setDescription(e.target.value)}
            className="w-full border rounded p-2 text-sm"
          />
        </div>
  
        {/* Image Upload with Validation */}
        <div>
          <label className="block text-sm font-medium mb-1">Upload Image</label>
          <input
            type="file"
            accept="image/png, image/jpeg"
            onChange={handleFileUpload}
            className="block text-sm"
          />
          <p className="text-xs text-gray-500 mt-1">
            Max 5 images, PNG/JPEG, up to 5 MB
          </p>
        </div>
      </div>
    );
  };
//________________________________________________________________________________________________________________________  

const renderPricingDetailsForProduct = () => {
  // Determine which price field to use (ignore null values)
  const validSalesPrice = sales_price_with_tax || sales_price_without_tax || "";

  return (
    <div className="space-y-6">
      {/* Sales Price */}
      <div className="grid grid-cols-1 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Sales Price</label>
          <div className="flex border rounded">
            <span className="flex items-center px-2 text-sm">₹</span>
            <input
              type="number"
              placeholder="200"
              value={validSalesPrice} // ✅ Use only the valid price field
              onChange={(e) => {
                if (withTax) {
                  setSalesPriceWithTax(e.target.value);
                  setSalesPriceWithoutTax(""); // Ensure only one field is set
                } else {
                  setSalesPriceWithoutTax(e.target.value);
                  setSalesPriceWithTax("");
                }
              }}
              className="w-full p-2 text-sm focus:outline-none"
            />
          </div>
        </div>
      </div>

      {/* Tax Selection */}
      <div className="flex space-x-4 mt-1 text-sm">
        <label className="flex items-center">
          <input
            type="radio"
            checked={withTax}
            onChange={() => {
              setWithTax(true);
              setSalesPriceWithoutTax(""); // Ensure `sales_price_without_tax` is cleared
            }}
            className="mr-1"
          />
          With Tax
        </label>
        <label className="flex items-center">
          <input
            type="radio"
            checked={!withTax}
            onChange={() => {
              setWithTax(false);
              setSalesPriceWithTax(""); // Ensure `sales_price_with_tax` is cleared
            }}
            className="mr-1"
          />
          No Tax
        </label>
      </div>

      {/* GST Tax Rate */}
      <div>
        <label className="block text-sm font-medium mb-1">GST Tax Rate (%)</label>
        <select
          value={gstTaxRate}
          onChange={(e) => setGstTaxRate(e.target.value)}
          className="w-full border rounded p-2 text-sm"
        >
          <option value="0">None</option>
          <option value="5">5%</option>
          <option value="12">12%</option>
          <option value="18">18%</option>
          <option value="28">28%</option>
        </select>
      </div>
    </div>
  );
};
//______________________________________________________________________________________________________

const renderBasicDetailsForService = () => {
  // Use the valid sales price field (avoid null values)
  const validSalesPrice = sales_price_with_tax || sales_price_without_tax || "";

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Item Type Selection */}
        <div>
          <label className="block text-sm font-medium mb-1">Item Type *</label>
          <div className="flex space-x-4">
            <label className="flex items-center text-sm">
              <input
                type="radio"
                name="itemType"
                value="Product"
                checked={itemType === "Product"}
                onChange={() => {
                  setItemType("Product");
                  setActiveTab(0);
                }}
                className="mr-1"
              />
              Product
            </label>
            <label className="flex items-center text-sm">
              <input
                type="radio"
                name="itemType"
                value="Service"
                checked={itemType === "Service"}
                onChange={() => {
                  setItemType("Service");
                  setActiveTab(0);
                }}
                className="mr-1"
              />
              Service
            </label>
          </div>
        </div>

        {/* Category Selection */}
        <div className="relative">
          <label className="block text-sm font-medium mb-1">Category</label>
          <button
            className="w-full border rounded p-2 text-left text-sm"
            onClick={() => setCreateItemCatDropdownOpen(!createItemCatDropdownOpen)}
          >
            {typeof itemCat === "object" ? itemCat.name : itemCat}
          </button>
          {createItemCatDropdownOpen && (
            <ul className="absolute z-10 mt-1 w-full bg-white border rounded shadow">
              {categories.map((cat, idx) => (
                <li
                  key={idx}
                  className="p-2 text-sm cursor-pointer hover:bg-gray-100"
                  onClick={() => {
                    setItemCat(cat);
                    setCreateItemCatDropdownOpen(false);
                  }}
                >
                  {cat.name}
                </li>
              ))}
              <li
                className="p-2 text-sm cursor-pointer font-semibold text-[#7B68EE] hover:bg-gray-100"
                onClick={handleOpenAddCatModalInCreateItem}
              >
                + Add Category
              </li>
            </ul>
          )}
        </div>
      </div>

      {/* Service Name & Online Store Option */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Service Name *</label>
          <input
            type="text"
            placeholder="ex: Mobile service"
            value={serviceName}
            onChange={(e) => setServiceName(e.target.value)}
            className="w-full border rounded p-2 text-sm"
          />
          {!serviceName.trim() && (
            <span className="text-xs text-red-500">Please enter the service name</span>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Show Item in Online Store</label>
          <div className="flex items-center h-10">
            <input
              type="checkbox"
              checked={showOnline}
              onChange={(e) => setShowOnline(e.target.checked)}
              className="h-4 w-4"
            />
            <span className="ml-2 text-sm">Enable</span>
          </div>
        </div>
      </div>

      {/* Sales Price & Tax Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Sales Price *</label>
          <input
            type="number"
            placeholder="₹200"
            value={validSalesPrice} // ✅ Use only the valid price
            onChange={(e) => {
              if (withTax) {
                setSalesPriceWithTax(e.target.value);
                setSalesPriceWithoutTax(""); // Ensure only one field is set
              } else {
                setSalesPriceWithoutTax(e.target.value);
                setSalesPriceWithTax("");
              }
            }}
            className="w-full border rounded p-2 text-sm"
          />
          <div className="flex space-x-4 mt-1 text-sm">
            <label className="flex items-center">
              <input
                type="radio"
                checked={withTax}
                onChange={() => {
                  setWithTax(true);
                  setSalesPriceWithoutTax(""); // Clear the other field
                }}
                className="mr-1"
              />
              With Tax
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                checked={!withTax}
                onChange={() => {
                  setWithTax(false);
                  setSalesPriceWithTax(""); // Clear the other field
                }}
                className="mr-1"
              />
              No Tax
            </label>
          </div>
        </div>

        {/* GST Tax Rate */}
        <div>
          <label className="block text-sm font-medium mb-1">GST Tax Rate (%)</label>
          <select
            value={gstTaxRate}
            onChange={(e) => setGstTaxRate(e.target.value)}
            className="w-full border rounded p-2 text-sm"
          >
            <option value="0">None</option>
            <option value="5">5%</option>
            <option value="12">12%</option>
            <option value="18">18%</option>
            <option value="28">28%</option>
          </select>
        </div>
      </div>

      {/* Measuring Unit & Service Code */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Measuring Unit</label>
          <select
            value={measuringUnit}
            onChange={(e) => setMeasuringUnit(e.target.value)}
            className="w-full border rounded p-2 text-sm"
          >
            {MeasuringUnits?.map((unit, index) => (
              <option key={index} value={unit}>{unit}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Service Code</label>
          <input
            type="text"
            placeholder="Enter Service Code"
            value={serviceCode}
            onChange={(e) => setServiceCode(e.target.value)}
            className="w-full border rounded p-2 text-sm"
          />
        </div>
      </div>
    </div>
  );
};
// __________________________________________________________________________________________________________________________

const fetchSacDescription = async (code) => {
  if (!code.trim()) {
    setDescription(""); // Clear description if SAC code is removed
    return;
  }

  try {
    const response = await axios.get(`${baseurl}/api/sac-codes/${code}/`);
    setDescription(response.data.description || ""); // Set description or clear if not found
  } catch (error) {
    console.error("Error fetching SAC Code description", error);
    setDescription(""); // Ensure description is cleared if API fails
  }
};

const renderOtherDetailsForService = () => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* SAC Code Input */}
        <div>
          <label className="block text-sm font-medium mb-1">SAC Code</label>
          <input
            type="text"
            placeholder="ex: 9983"
            value={sacCode}
            onChange={(e) => {
              setSacCode(e.target.value);
              fetchSacDescription(e.target.value); // Fetch description dynamically
            }}
            className="w-full border rounded p-2 text-sm"
          />
        </div>

        {/* Find SAC Code Button */}
        <div className="flex items-end">
          <button className="px-2 py-1 border rounded text-sm flex items-center space-x-1 hover:bg-gray-100">
            <Search size={14} />
            <span>Find SAC Code</span>
          </button>
        </div>
      </div>

      {/* Description (Auto-Filled from Backend if SAC Code is Valid) */}
      <div>
        <label className="block text-sm font-medium mb-1">Description</label>
        <textarea
          placeholder="Enter Description"
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full border rounded p-2 text-sm"
        />
      </div>
    </div>
  );
};

// No Changes Needed for Other Parts
const renderPartyWiseForService = () => (
  <div className="text-sm p-4">Party Wise Rates (Service) content here...</div>
);
const renderCustomForService = () => (
  <div className="text-sm p-4">Custom Fields (Service) content here...</div>
);

// Decides what to show in the right panel of Create Item Modal
const renderRightContent = () => {
  if (itemType === "Product") {
    switch (activeTab) {
      case 0:
        return renderBasicDetailsForProduct();
      case 1:
        return renderStockDetailsForProduct();
      case 2:
        return renderPricingDetailsForProduct();
      case 3:
        return renderPartyWiseForProduct();
      case 4:
        return renderCustomForProduct();
      default:
        return null;
    }
  } else {
    switch (activeTab) {
      case 0:
        return renderBasicDetailsForService();
      case 1:
        return renderOtherDetailsForService();
      case 2:
        return renderPartyWiseForService();
      case 3:
        return renderCustomForService();
      default:
        return null;
    }
  }
};
// ________________________________________________________________________________________________________________________________________
  // ------------------------------------------------
  // 6) Detail View State
  // ------------------------------------------------
  const [detailView, setDetailView] = useState(false);
  const [detailTab, setDetailTab] = useState(0);
  const [selectedItemIndex, setSelectedItemIndex] = useState(null);
  const [detailSearchTerm, setDetailSearchTerm] = useState("");

  const handleRowClick = (index) => {
    setSelectedItemIndex(index);
    setDetailView(true);
    setDetailTab(0);
    setDetailSearchTerm("");
  };
  const closeDetailView = () => {
    setDetailView(false);
    setSelectedItemIndex(null);
  };

  const getItemName = (item) => {
    return item.type === "Product" ? item.itemName : item.serviceName;
  };
  const getItemStockQty = (item) => {
    if (item.type === "Product" && item.openingStock) {
      const parsed = parseFloat(item.openingStock);
      return isNaN(parsed) ? 0 : parsed;
    }
    return 0;
  };

  const renderDetailView = () => {
    if (selectedItemIndex === null) return null;
  
    const currentItem = items[selectedItemIndex];
    const stockQty = getItemStockQty(currentItem);
    const isOutOfStock = stockQty <= 0;
    const itemLabel = getItemName(currentItem) || "(unnamed)";
  
    // Ensure correct price mapping (ignore null values)
    const validSalesPrice =
      currentItem.sales_price_with_tax || currentItem.sales_price_without_tax || "-";
  
    const formatPrice = (price, isWithTax) => {
      if (!price) return "₹ 0";
      return isWithTax ? `₹ ${price} With Tax` : `₹ ${price}`;
    };
  
    return (
      <>
        <div className="flex bg-[#F9FAFB] min-h-screen">
          <div className="w-64 bg-white border-r flex flex-col p-4 space-y-4">
            {/* Search Bar */}
            <input
              type="text"
              placeholder="Search Item"
              value={detailSearchTerm}
              onChange={(e) => setDetailSearchTerm(e.target.value)}
              className="border rounded p-2 text-sm"
            />
            <div className="flex-1 overflow-auto">
              {items
                .filter((it) =>
                  getItemName(it).toLowerCase().includes(detailSearchTerm.toLowerCase())
                )
                .map((it, idx) => {
                  const name = getItemName(it) || "(unnamed)";
                  const qty = getItemStockQty(it);
                  return (
                    <div
                      key={idx}
                      onClick={() => {
                        setSelectedItemIndex(items.indexOf(it));
                        setDetailTab(0);
                      }}
                      className={`cursor-pointer mb-2 p-2 rounded hover:bg-gray-100 ${
                        items.indexOf(it) === selectedItemIndex ? "bg-gray-200" : ""
                      }`}
                    >
                      <div className="font-medium text-sm">{name}</div>
                      <div className="text-xs text-gray-500">
                        {qty} {it.measuringUnit || "PCS"}
                      </div>
                    </div>
                  );
                })}
            </div>
            <div className="text-xs text-gray-500">Stock Value: 0</div>
          </div>
  
          {/* Right Detail View */}
          <div className="flex-1 flex flex-col">
            <div className="flex items-center justify-between border-b p-4 bg-white">
              <div className="flex items-center space-x-4">
                <h2 className="text-xl font-semibold">{itemLabel}</h2>
                {isOutOfStock ? (
                  <span className="text-sm bg-red-100 text-red-600 px-2 py-1 rounded">
                    Out of Stock
                  </span>
                ) : (
                  <span className="text-sm bg-green-100 text-green-600 px-2 py-1 rounded">
                    In Stock
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <button className="px-3 py-1 border rounded text-sm hover:bg-gray-100">
                  Adjust Stock
                </button>
                <button
                  className="px-3 py-1 border rounded text-sm hover:bg-gray-100"
                  onClick={() => handleEditItem(selectedItemIndex)}
                >
                  Edit
                </button>
                <button
                  className="px-3 py-1 border rounded text-sm hover:bg-gray-100"
                  onClick={handleDeleteItem}
                >
                  Delete
                </button>
                <button
                  className="px-3 py-1 bg-gray-300 text-sm rounded"
                  onClick={closeDetailView}
                >
                  Close
                </button>
              </div>
            </div>
  
            {/* Tabs */}
            <div className="flex items-center space-x-6 px-4 py-2 border-b bg-white">
              <button
                className={`text-sm pb-2 ${
                  detailTab === 0
                    ? "border-b-2 border-[#7B68EE] text-[#7B68EE]"
                    : "text-gray-600"
                }`}
                onClick={() => setDetailTab(0)}
              >
                Item Details
              </button>
              <button
                className={`text-sm pb-2 ${
                  detailTab === 1
                    ? "border-b-2 border-[#7B68EE] text-[#7B68EE]"
                    : "text-gray-600"
                }`}
                onClick={() => setDetailTab(1)}
              >
                Stock Details
              </button>
              <button
                className={`text-sm pb-2 ${
                  detailTab === 2
                    ? "border-b-2 border-[#7B68EE] text-[#7B68EE]"
                    : "text-gray-600"
                }`}
                onClick={() => setDetailTab(2)}
              >
                Party Wise Report
              </button>
              <button
                className={`text-sm pb-2 ${
                  detailTab === 3
                    ? "border-b-2 border-[#7B68EE] text-[#7B68EE]"
                    : "text-gray-600"
                }`}
                onClick={() => setDetailTab(3)}
              >
                Party Wise Prices
              </button>
            </div>
  
            {/* Content */}
            <div className="flex-1 overflow-auto">{renderRightTabContent()}</div>
          </div>
        </div>
      </>
    );
  };
  // ___________________________________________________________________________________________________________________________________
  const renderMainContent = () => {
    return (
      <div className="h-screen overflow-auto">
        <div className="max-w-7xl mx-auto p-4 space-y-6 font-sans ">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Items</h2>
            <div className="flex items-center space-x-2">
              {/* Reports Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setReportsOpen(!reportsOpen)}
                  className="px-3 py-1 bg-[#7B68EE] text-white rounded text-sm hover:bg-[#6959CD]"
                >
                  Reports
                </button>
                {reportsOpen && (
                  <div className="absolute right-0 mt-1 w-48 bg-white border rounded shadow text-sm">
                    <button
                      className="block w-full text-left px-4 py-2 text-[#7B68EE] hover:bg-[#7B68EE] hover:text-white"
                      onClick={() => {
                        setSelectedReport("rate-list");
                        setReportsOpen(false);
                      }}
                    >
                      Rate List
                    </button>
                    <button
                      className="block w-full text-left px-4 py-2 text-[#7B68EE] hover:bg-[#7B68EE] hover:text-white"
                      onClick={() => {
                        setSelectedReport("stock-summary");
                        setReportsOpen(false);
                      }}
                    >
                      Stock Summary
                    </button>
                    <button
                      className="block w-full text-left px-4 py-2 text-[#7B68EE] hover:bg-[#7B68EE] hover:text-white"
                      onClick={() => {
                        setSelectedReport("low-stock-summary");
                        setReportsOpen(false);
                      }}
                    >
                      Low Stock Summary
                    </button>
                    <button
                      className="block w-full text-left px-4 py-2 text-[#7B68EE] hover:bg-[#7B68EE] hover:text-white"
                      onClick={() => {
                        setSelectedReport("item-sales-summary");
                        setReportsOpen(false);
                      }}
                    >
                      Item Sales Summary
                    </button>
                  </div>
                )}
              </div>
              <button className="p-2 border rounded">
                <Layout size={16} />
              </button>
              <button className="p-2 border rounded">
                <LayoutGrid size={16} />
              </button>
            </div>
          </div>
  
          {/* Table */}
          <div className="border rounded p-4 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-2 text-left">Item Name</th>
                  <th className="p-2 text-left">Item Code</th>
                  <th className="p-2 text-left">Stock QTY</th>
                  <th className="p-2 text-left">Selling Price</th>
                  <th className="p-2 text-left">Purchase Price</th>
                </tr>
              </thead>
              <tbody>
                {listItems.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="text-center text-gray-500">
                      No items found
                    </td>
                  </tr>
                ) : (
                  listItems.map((it, i) => {
                    // Ensure correct item name mapping
                    const displayName =
                      it.type === "product" ? it.item_name : it.service_name;
  
                    // Ensure correct item code mapping
                    const itemCodeVal =
                      it.type === "product"
                        ? it.product_code // Corrected for products
                        : it.service_code; // Corrected for services
  
                    // Ensure correct stock quantity
                    const stockQty =
                      it.type === "product" && it.opening_stock
                        ? `${it.opening_stock} ${it.measuring_unit || ""}`
                        : "-";
  
                    // Ensure correct price mapping
                    const priceLabel =
                      it.sales_price_with_tax || it.sales_price_without_tax
                        ? `₹ ${it.sales_price_with_tax || it.sales_price_without_tax}`
                        : "-";
  
                    // Ensure correct purchase price mapping
                    const purchasePriceLabel = it.purchase_price
                      ? `₹ ${it.purchase_price}`
                      : "-";
  
                    // Ensure category name is handled properly
                    const categoryName = it.category || "-";
  
                    return (
                      <tr
                        key={i}
                        className="border-b cursor-pointer hover:bg-gray-50"
                        onClick={() => handleRowClick(i)}
                      >
                        <td className="p-2">
                          {displayName || "(unnamed)"}
                          {categoryName && (
                            <div className="text-xs text-gray-500">{categoryName}</div>
                          )}
                        </td>
                        <td className="p-2">{itemCodeVal || "-"}</td>
                        <td className="p-2">{stockQty}</td>
                        <td className="p-2">{priceLabel}</td>
                        <td className="p-2">{purchasePriceLabel}</td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };
  // _______________________________________________________________________________________________________________________________________
  // ------------------------------------------------
  // NEW CODE: REPORT SELECTION & REPORT PAGES
  // ------------------------------------------------
  function RenderReportView({ route, items, categories, onBack }) {
    let reportComponent = null;
    switch (route) {
      case "rate-list":
        reportComponent = <RateList items={items} categories={categories} />;
        break;
      case "stock-summary":
        reportComponent = <StockSummary items={items} categories={categories} />;
        break;
      case "low-stock-summary":
        reportComponent = <LowStockSummary items={items} categories={categories} />;
        break;
      case "item-sales-summary":
        reportComponent = <ItemSalesSummary items={items} categories={categories} />;
        break;
      default:
        reportComponent = null;
    }
    return (
      <div className="max-w-7xl mx-auto p-4">
        <button
          onClick={onBack}
          className="mb-4 px-3 py-1 border rounded text-sm hover:bg-gray-100"
        >
          &larr; Back to Items
        </button>
        {reportComponent}
      </div>
    );
  }
  
  function RateList({ items, categories }) {
    const filteredItems = items.map((it) => ({
      name: it.type === "product" ? it.item_name : it.service_name,
      code: it.type === "product" ? it.product_code : it.service_code || "SRV",
      mrp: it.mrp || "-",
      sellingPrice: it.sales_price_with_tax || it.sales_price_without_tax || "-",
    }));
  
    return (
      <div className="max-w-7xl mx-auto p-4 space-y-6 font-sans">
        <h2 className="text-2xl font-bold mb-4">Rate List Report</h2>
        <div className="border rounded p-4 overflow-auto bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 text-left">Name</th>
                <th className="p-2 text-left">Item Code</th>
                <th className="p-2 text-left">MRP</th>
                <th className="p-2 text-left">Selling Price</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan="4" className="text-center text-gray-500">
                    No data available.
                  </td>
                </tr>
              ) : (
                filteredItems.map((it, i) => (
                  <tr key={i} className="border-b">
                    <td className="p-2">{it.name}</td>
                    <td className="p-2">{it.code}</td>
                    <td className="p-2">₹ {it.mrp}</td>
                    <td className="p-2">₹ {it.sellingPrice}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
  
  function LowStockSummary({ items }) {
    const lowStockItems = items.filter((it) => it.type === "product" && it.opening_stock < it.stock_threshold);
  
    return (
      <div className="max-w-7xl mx-auto p-4 space-y-6 font-sans">
        <h2 className="text-2xl font-bold mb-4">Low Stock Summary Report</h2>
        <div className="border rounded p-4 overflow-auto bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 text-left">Item Name</th>
                <th className="p-2 text-left">Item Code</th>
                <th className="p-2 text-left">Stock Qty</th>
                <th className="p-2 text-left">Low Stock Level</th>
                <th className="p-2 text-left">Stock Value</th>
              </tr>
            </thead>
            <tbody>
              {lowStockItems.length === 0 ? (
                <tr>
                  <td colSpan="5" className="text-center text-gray-500">
                    All items have sufficient stock.
                  </td>
                </tr>
              ) : (
                lowStockItems.map((it, i) => (
                  <tr key={i} className="border-b">
                    <td className="p-2">{it.item_name}</td>
                    <td className="p-2">{it.product_code || "-"}</td>
                    <td className="p-2">{it.opening_stock || 0}</td>
                    <td className="p-2">{it.stock_threshold || "N/A"}</td>
                    <td className="p-2">₹ {it.opening_stock * (it.purchase_price || 0)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
  
  function StockSummary({ items }) {
    const filteredItems = items.map((it) => ({
      name: it.type === "product" ? it.item_name : it.service_name,
      code: it.type === "product" ? it.product_code : it.service_code || "SRV",
      purchasePrice: it.purchase_price || "-",
      sellingPrice: it.sales_price_with_tax || it.sales_price_without_tax || "-",
      stockQty: it.type === "product" ? `${it.opening_stock || 0} ${it.measuring_unit || ""}` : "-",
      stockValue: it.opening_stock * (it.purchase_price || 0),
    }));
  
    return (
      <div className="max-w-7xl mx-auto p-4 space-y-6 font-sans">
        <h2 className="text-2xl font-bold mb-4">Stock Summary Report</h2>
        <div className="border rounded p-4 overflow-auto bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 text-left">Item Name</th>
                <th className="p-2 text-left">Item Code</th>
                <th className="p-2 text-left">Purchase Price</th>
                <th className="p-2 text-left">Selling Price</th>
                <th className="p-2 text-left">Stock Qty</th>
                <th className="p-2 text-left">Stock Value</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center text-gray-500">
                    No data available.
                  </td>
                </tr>
              ) : (
                filteredItems.map((it, i) => (
                  <tr key={i} className="border-b">
                    <td className="p-2">{it.name}</td>
                    <td className="p-2">{it.code}</td>
                    <td className="p-2">₹ {it.purchasePrice}</td>
                    <td className="p-2">₹ {it.sellingPrice}</td>
                    <td className="p-2">{it.stockQty}</td>
                    <td className="p-2">₹ {it.stockValue}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  }