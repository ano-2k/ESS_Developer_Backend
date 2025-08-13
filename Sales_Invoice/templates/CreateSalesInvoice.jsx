import React, { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

// Indian states array
const indianStates = [
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
  "Andaman and Nicobar Islands",
  "Chandigarh",
  "Dadra & Nagar Haveli and Daman & Diu",
  "Delhi",
  "Jammu and Kashmir",
  "Lakshadweep",
  "Puducherry",
];

// Extended tax dropdown options
const taxOptions = [
  { label: "None", value: 0 },
  { label: "Exempted", value: 0 },
  { label: "GST @ 0%", value: 0 },
  { label: "GST @ 0.1%", value: 0.1 },
  { label: "GST @ 0.25%", value: 0.25 },
  { label: "GST @ 1.5%", value: 1.5 },
  { label: "GST @ 3%", value: 3 },
  { label: "GST @ 5%", value: 5 },
  { label: "GST @ 12%", value: 12 },
  { label: "GST @ 13.8%", value: 13.8 },
  { label: "GST @ 14% + cess @ 12%", value: 26 },
  { label: "GST @ 28%", value: 28 },
  { label: "GST @ 28% + Cess @ 12%", value: 40 },
  { label: "GST @ 28% + Cess @ 60%", value: 88 },
];

const CreateSalesInvoice = () => {
  // ------------------------------------------------------------------
  // 1) Party & Shipping Setup
  // ------------------------------------------------------------------
  const location = useLocation();
  const navigate = useNavigate();

  // Pull query params for partyId, invoiceId, and view
  const searchParams = new URLSearchParams(location.search);
  const partyId = searchParams.get("partyId");
  const invoiceId = searchParams.get("invoiceId");
  const viewParam = searchParams.get("view");

  const [parties, setParties] = useState([]);
  const [selectedParty, setSelectedParty] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [showPartyDropdown, setShowPartyDropdown] = useState(false);

  const [showChangeShippingModal, setShowChangeShippingModal] = useState(false);
  const [showEditShippingModal, setShowEditShippingModal] = useState(false);
  const [shippingAddresses, setShippingAddresses] = useState([]);
  const [editingAddress, setEditingAddress] = useState(null);

  const [showNotes, setShowNotes] = useState(false);
  const [showTerms, setShowTerms] = useState(false);
  const [showNewAccountModal, setShowNewAccountModal] = useState(false);

  // Bank account fields
  const [accountName, setAccountName] = useState("");
  const [openingBalance, setOpeningBalance] = useState("");
  const [asOfDate, setAsOfDate] = useState("");
  const [bankAccountNumber, setBankAccountNumber] = useState("");
  const [reEnterBankAccountNumber, setReEnterBankAccountNumber] = useState("");
  const [ifscCode, setIfscCode] = useState("");
  const [bankBranch, setBankBranch] = useState("");
  const [accountHolderName, setAccountHolderName] = useState("");
  const [upiId, setUpiId] = useState("");

  const [showAdditionalCharge, setShowAdditionalCharge] = useState(false);
  const [showDiscount, setShowDiscount] = useState(false);

  // ------------------------------------------------------------------
  // 2) Check if we're in "preview" mode
  // ------------------------------------------------------------------
  const [savedInvoice, setSavedInvoice] = useState(null);
  const [showInvoicePreview, setShowInvoicePreview] = useState(false);

  // If invoiceId + view=1 => load that invoice from localStorage
  // and show preview
  useEffect(() => {
    if (invoiceId && viewParam === "1") {
      const allInvoices = JSON.parse(localStorage.getItem("invoices")) || [];
      const existing = allInvoices.find((inv) => String(inv.id) === invoiceId);
      if (existing) {
        setSavedInvoice(existing);
        setShowInvoicePreview(true);
      }
    }
  }, [invoiceId, viewParam]);

  // ------------------------------------------------------------------
  // 3) Load Party from localStorage if partyId is present
  // ------------------------------------------------------------------
  useEffect(() => {
    const storedParties = JSON.parse(localStorage.getItem("parties")) || [];
    setParties(storedParties);

    let foundParty = null;
    if (partyId) {
      foundParty = storedParties.find((p) => String(p.id) === partyId);
      if (!foundParty) {
        const idx = parseInt(partyId, 10);
        if (!isNaN(idx) && storedParties[idx]) {
          foundParty = storedParties[idx];
        }
      }
    }
    if (!foundParty && location.state?.party) {
      foundParty = location.state.party;
    }
    if (foundParty) {
      setSelectedParty(foundParty);
      setShippingAddresses(foundParty.shippingAddresses || []);
    }
  }, [partyId, location.state]);

  const filteredParties = parties.filter((p) =>
    p.party_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelectParty = (p) => {
    setSelectedParty(p);
    setShowPartyDropdown(false);
    setShippingAddresses(p.shippingAddresses || []);
  };

  const updatePartyInLocalStorage = (updatedParty) => {
    const all = JSON.parse(localStorage.getItem("parties")) || [];
    const newList = all.map((partyObj) =>
      partyObj.id === updatedParty.id ? updatedParty : partyObj
    );
    localStorage.setItem("parties", JSON.stringify(newList));
    setParties(newList);
    setSelectedParty(updatedParty);
    setShippingAddresses(updatedParty.shippingAddresses || []);
  };

  // ------------------------------------------------------------------
  // Shipping Address Handling
  // ------------------------------------------------------------------
  const handleChangeShippingAddress = () => {
    if (!selectedParty || selectedParty.id == null) {
      alert("No party selected. Please select a party first.");
      return;
    }
    setShowChangeShippingModal(true);
  };

  const handleAddNewShippingAddress = () => {
    setEditingAddress({ name: "", street: "", state: "", pincode: "", city: "" });
    setShowEditShippingModal(true);
  };

  const handleEditShippingAddress = (address) => {
    setEditingAddress({ ...address });
    setShowEditShippingModal(true);
  };

  const handleSelectShippingAddress = (address) => {
    const updatedParty = {
      ...selectedParty,
      shipping: formatAddressString(address),
    };
    updatePartyInLocalStorage(updatedParty);
  };

  const handleDoneShipping = () => {
    setShowChangeShippingModal(false);
  };

  const formatAddressString = (addr) => {
    return `${addr.name}\n${addr.street}\n${addr.city}, ${addr.state} - ${addr.pincode}`;
  };

  const handlePincodeChange = async (e) => {
    const pin = e.target.value;
    setEditingAddress({ ...editingAddress, pincode: pin });
    if (pin.length === 6) {
      try {
        const res = await fetch(`https://api.postalpincode.in/pincode/${pin}`);
        const data = await res.json();
        if (data && data[0].Status === "Success") {
          const cityName = data[0].PostOffice[0].District || "";
          setEditingAddress({
            ...editingAddress,
            pincode: pin,
            city: cityName,
          });
        }
      } catch (err) {
        console.log("Error fetching city:", err);
      }
    }
  };

  const handleSaveShippingAddress = () => {
    if (!editingAddress.name || !editingAddress.street) {
      alert("Shipping Name and Street Address are required.");
      return;
    }
    let updatedAddresses = [...shippingAddresses];
    if (!editingAddress.id) {
      editingAddress.id = Date.now();
      updatedAddresses.push(editingAddress);
    } else {
      updatedAddresses = updatedAddresses.map((addr) =>
        addr.id === editingAddress.id ? editingAddress : addr
      );
    }
    const updatedParty = {
      ...selectedParty,
      shippingAddresses: updatedAddresses,
      shipping: formatAddressString(editingAddress),
    };
    updatePartyInLocalStorage(updatedParty);
    setShowEditShippingModal(false);
  };

  const renderShippingAddress = () => {
    if (!selectedParty?.shipping) return "[No shipping address set]";
    return selectedParty.shipping.split("\n").map((line, idx) => (
      <span key={idx} className="block">
        {line}
      </span>
    ));
  };

  // ------------------------------------------------------------------
  // Buttons
  // ------------------------------------------------------------------
  const handleScanBarcode = () => alert("Scan Barcode clicked!");
  const handleSettings = () => alert("Settings clicked!");
  const handleSaveAndNew = () => alert("Save & New clicked!");

  // ------------------------------------------------------------------
  // Invoice Items & Calculations
  // ------------------------------------------------------------------
  const [invoiceItems, setInvoiceItems] = useState([]);
  const [subtotal, setSubtotal] = useState(0);
  const [taxTotal, setTaxTotal] = useState(0);
  const [discountTotal, setDiscountTotal] = useState(0);

  const [additionalCharge, setAdditionalCharge] = useState(0);
  const [additionalChargeTaxRate, setAdditionalChargeTaxRate] = useState(0);
  const [discountAfterTax, setDiscountAfterTax] = useState(0);
  const [discountAfterTaxIsPercent, setDiscountAfterTaxIsPercent] = useState(true);

  const [autoRoundOff, setAutoRoundOff] = useState(false);
  const [roundOffValue, setRoundOffValue] = useState(0);

  const [grandTotal, setGrandTotal] = useState(0);
  const [exceedsCreditLimit, setExceedsCreditLimit] = useState(false);
  const [markAsFullyPaid, setMarkAsFullyPaid] = useState(false);

  useEffect(() => {
    calculateTotals();
  }, [
    invoiceItems,
    additionalCharge,
    additionalChargeTaxRate,
    discountAfterTax,
    discountAfterTaxIsPercent,
    autoRoundOff,
    roundOffValue,
  ]);

  useEffect(() => {
    if (selectedParty && selectedParty.creditLimit) {
      setExceedsCreditLimit(grandTotal > selectedParty.creditLimit);
    } else {
      setExceedsCreditLimit(false);
    }
  }, [grandTotal, selectedParty]);

  const calculateTotals = () => {
    let sub = 0;
    let tax = 0;
    let disc = 0;
    invoiceItems.forEach((item) => {
      const qty = parseFloat(item.qty || 0);
      const price = parseFloat(item.salesPrice || 0);
      const lineSubtotal = qty * price;
      sub += lineSubtotal;
      const itemTax = parseFloat(item.tax || 0);
      const itemDisc = parseFloat(item.discount || 0);
      tax += (lineSubtotal * itemTax) / 100;
      disc += (lineSubtotal * itemDisc) / 100;
    });

    let newTotal = sub + tax - disc;

    // Additional charge
    const addChargeVal = parseFloat(additionalCharge) || 0;
    const addChargeTax =
      (addChargeVal * parseFloat(additionalChargeTaxRate || 0)) / 100;
    newTotal += addChargeVal + addChargeTax;

    // Discount after tax
    const afterTaxDisc = parseFloat(discountAfterTax) || 0;
    if (afterTaxDisc > 0) {
      newTotal -= discountAfterTaxIsPercent
        ? (newTotal * afterTaxDisc) / 100
        : afterTaxDisc;
    }

    // Auto round off
    if (autoRoundOff) {
      const roundVal = parseFloat(roundOffValue) || 0;
      newTotal = Math.round(newTotal + roundVal);
    }

    if (newTotal < 0) newTotal = 0;

    setSubtotal(sub);
    setTaxTotal(tax);
    setDiscountTotal(disc);
    setGrandTotal(newTotal);
  };

  const balanceAmount = markAsFullyPaid ? 0 : grandTotal;

  // ------------------------------------------------------------------
  // 4) Load itemCategories from localStorage
  // ------------------------------------------------------------------
  const [itemCategories, setItemCategories] = useState([]);
  useEffect(() => {
    const storedCats = JSON.parse(localStorage.getItem("itemCategories")) || [];
    const catNames = storedCats.map((c) => (typeof c === "string" ? c : c.name));
    setItemCategories(catNames);
  }, []);

  // ------------------------------------------------------------------
  // 5) Add Items Modal
  // ------------------------------------------------------------------
  const [showAddItemsModal, setShowAddItemsModal] = useState(false);
  const [allItems, setAllItems] = useState([]);
  const [itemSearchTerm, setItemSearchTerm] = useState("");
  const [itemCategoryFilter, setItemCategoryFilter] = useState("Select Category");
  const [modalQuantities, setModalQuantities] = useState({});

  useEffect(() => {
    const loadedItems = JSON.parse(localStorage.getItem("items")) || [];
    setAllItems(loadedItems);
  }, []);

  const handleOpenAddItemsModal = () => {
    setShowAddItemsModal(true);
  };
  const handleCloseAddItemsModal = () => {
    setShowAddItemsModal(false);
    setItemSearchTerm("");
    setItemCategoryFilter("Select Category");
    setModalQuantities({});
  };

  const filteredModalItems = allItems.filter((it) => {
    const name = it.type === "Product" ? it.itemName : it.serviceName;
    const category = it.category || "";
    const matchName = name?.toLowerCase().includes(itemSearchTerm.toLowerCase());
    const matchCategory =
      itemCategoryFilter === "Select Category" || itemCategoryFilter === category;
    return matchName && matchCategory;
  });

  const handleChangeModalQuantity = (index, qty) => {
    setModalQuantities((prev) => ({ ...prev, [index]: qty }));
  };

  const handleCreateNewItem = () => {
    // Navigate to Items page create item
    navigate("/items?createNew=1");
  };

  const handleDoneAddingItems = () => {
    const selectedItems = [];
    filteredModalItems.forEach((it, idx) => {
      const q = parseFloat(modalQuantities[idx] || 0);
      if (q > 0) {
        selectedItems.push({
          ...it,
          qty: q,
          discount: 0,
          tax: 0,
        });
      }
    });
    if (selectedItems.length > 0) {
      setInvoiceItems((prev) => [...prev, ...selectedItems]);
    }
    handleCloseAddItemsModal();
  };

  // ------------------------------------------------------------------
  // 6) Invoice Table & Edits
  // ------------------------------------------------------------------
  const handleAddItem = () => {
    handleOpenAddItemsModal();
  };
  const handleQtyChange = (idx, newQty) => {
    const updated = [...invoiceItems];
    updated[idx] = { ...updated[idx], qty: newQty };
    setInvoiceItems(updated);
  };
  const handlePriceChange = (idx, newPrice) => {
    const updated = [...invoiceItems];
    updated[idx] = { ...updated[idx], salesPrice: newPrice };
    setInvoiceItems(updated);
  };
  const handleDiscountChange = (idx, newDisc) => {
    const updated = [...invoiceItems];
    updated[idx] = { ...updated[idx], discount: newDisc };
    setInvoiceItems(updated);
  };
  const handleTaxChange = (idx, newTaxLabel) => {
    const option = taxOptions.find((o) => o.label === newTaxLabel);
    const numericRate = option ? option.value : 0;
    const updated = [...invoiceItems];
    updated[idx] = { ...updated[idx], tax: numericRate };
    setInvoiceItems(updated);
  };
  const handleRemoveInvoiceItem = (idx) => {
    const updated = [...invoiceItems];
    updated.splice(idx, 1);
    setInvoiceItems(updated);
  };

  // ------------------------------------------------------------------
  // 7) Save => store invoice => show preview
  // ------------------------------------------------------------------
  const [invoiceNumber, setInvoiceNumber] = useState(8);
  const [invoiceDate, setInvoiceDate] = useState(new Date().toLocaleDateString());
  const [dueDate, setDueDate] = useState("");

  const handleSave = () => {
    // If fully paid => set receivedAmount = grandTotal, else 0
    const receivedAmount = markAsFullyPaid ? grandTotal : 0;

    const invoiceData = {
      id: Date.now(),
      invoiceNumber,
      invoiceDate,
      dueDate,
      party: selectedParty,
      items: invoiceItems,
      subtotal,
      taxTotal,
      discountTotal,
      grandTotal,
      isFullyPaid: markAsFullyPaid,
      balanceAmount: markAsFullyPaid ? 0 : grandTotal,
      // New field to track how much is actually received
      receivedAmount,
    };

    let allInvoices = JSON.parse(localStorage.getItem("invoices")) || [];
    allInvoices.push(invoiceData);
    localStorage.setItem("invoices", JSON.stringify(allInvoices));
    setSavedInvoice(invoiceData);
    setShowInvoicePreview(true);
  };

  // We'll capture the invoice preview HTML via a ref
  const invoiceRef = useRef(null);

  // For the "delete invoice" confirmation modal
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleConfirmDelete = () => {
    let all = JSON.parse(localStorage.getItem("invoices")) || [];
    const updated = all.filter((inv) => inv.id !== savedInvoice.id);
    localStorage.setItem("invoices", JSON.stringify(updated));
    setShowInvoicePreview(false);
    setSavedInvoice(null);
    setShowDeleteModal(false);
    alert("Invoice deleted!");
    navigate("/salesinvoice")
  };

  // Download the same layout as PDF
  const handleDownloadPDF = async () => {
    if (!invoiceRef.current) return;

    const canvas = await html2canvas(invoiceRef.current, {
      scale: 2, // sharper text
    });
    const imgData = canvas.toDataURL("image/png");

    const pdf = new jsPDF("p", "pt", "a4");
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();

    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;
    const ratio = canvasHeight / canvasWidth;
    const newHeight = pdfWidth * ratio;

    pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, newHeight);
    pdf.save(`invoice_${savedInvoice.invoiceNumber}.pdf`);
  };

  // ------------------------------------------------------------------
  // 8) If we're in preview mode, show invoice preview
  // ------------------------------------------------------------------
  if (showInvoicePreview && savedInvoice) {
    const isPaid = savedInvoice.balanceAmount === 0;

    return (
      <>
        {/* TOP BAR => Invoice #, Paid/Unpaid, Download, Print, etc. */}
        <div className="p-4 flex items-center justify-between border-b bg-white ">
          <div className="flex items-center space-x-2">
            <h2 className="text-xl font-semibold">
              Sales Invoice #{savedInvoice.invoiceNumber}
            </h2>
            <span
              className={`text-sm px-2 py-1 rounded ${
                isPaid
                  ? "bg-green-100 text-green-600"
                  : "bg-red-100 text-red-600"
              }`}
            >
              {isPaid ? "Paid" : "Unpaid"}
            </span>
          </div>
          <div className="space-x-2">
            <button
              onClick={handleDownloadPDF}
              className="px-3 py-1 border rounded hover:bg-gray-100 text-sm"
            >
              Download PDF
            </button>
            <button
              onClick={() => window.print()}
              className="px-3 py-1 border rounded hover:bg-gray-100 text-sm"
            >
              Print PDF
            </button>
            <button
              onClick={() => alert("Generate E-way Bill clicked!")}
              className="px-3 py-1 border rounded hover:bg-gray-100 text-sm"
            >
              Generate E-way Bill
            </button>
            <button
              onClick={() => alert("Generate E-invoice clicked!")}
              className="px-3 py-1 border rounded hover:bg-gray-100 text-sm"
            >
              Generate E-invoice
            </button>
          </div>
        </div>

        {/* EDIT / DELETE */}
        <div className="p-4 flex items-center justify-end space-x-2 border-b bg-white ">
          <button
            onClick={() => {
              // Reopen the form with saved invoice data
              setInvoiceItems(savedInvoice.items);
              setInvoiceNumber(savedInvoice.invoiceNumber);
              setInvoiceDate(savedInvoice.invoiceDate);
              setDueDate(savedInvoice.dueDate);
              setSelectedParty(savedInvoice.party);
              setSubtotal(savedInvoice.subtotal);
              setTaxTotal(savedInvoice.taxTotal);
              setDiscountTotal(savedInvoice.discountTotal);
              setGrandTotal(savedInvoice.grandTotal);
              setMarkAsFullyPaid(savedInvoice.isFullyPaid);

              setShowInvoicePreview(false);
            }}
            className="px-3 py-1 border rounded hover:bg-gray-100 text-sm"
          >
            Edit
          </button>
          <button
            onClick={() => setShowDeleteModal(true)}
            className="px-3 py-1 border rounded hover:bg-gray-100 text-sm text-red-500"
          >
            Delete
          </button>
        </div>

        {/* INVOICE PREVIEW SECTION */}
        <div
          className="max-w-4xl bg-white p-4 mt-4 ml-64 border border-gray-300 overflow-y-auto"
          style={{ maxHeight: "calc(100vh - 200px)" }}
          ref={invoiceRef}
        >
          {/* Top Row */}
          <div className="flex justify-between border-b pb-2 mb-2">
            <div className="font-bold uppercase text-sm">BILL OF SUPPLY</div>
            <div className="font-bold uppercase text-sm">ORIGINAL FOR RECIPIENT</div>
          </div>

          {/* Business Name / Mobile */}
          <div className="text-center mb-4">
            <div className="text-lg font-bold">Business Name</div>
            <div className="text-sm">Mobile: 7010738782</div>
          </div>

          {/* Bill To & Invoice Info */}
          <div className="flex justify-between border-b pb-2 mb-4 text-sm">
            {/* Left side: Bill To */}
            <div>
              <div className="font-semibold">BILL TO</div>
              <div>{savedInvoice.party?.party_name || "CASH SALE"}</div>
              <div>Mobile: {savedInvoice.party?.mobile_number || "1234567890"}</div>
            </div>
            {/* Right side: Invoice details */}
            <div className="text-right">
              <div>Invoice No: {savedInvoice.invoiceNumber}</div>
              <div>Invoice Date: {savedInvoice.invoiceDate}</div>
              <div>Due Date: {savedInvoice.dueDate || "05/03/2025"}</div>
            </div>
          </div>

          {/* Items Table */}
          <table className="w-full text-sm border border-gray-300 mb-2">
            <thead className="border-b bg-gray-100">
              <tr>
                <th className="p-2 border-r">S.NO</th>
                <th className="p-2 border-r">SERVICES</th>
                <th className="p-2 border-r">QTY.</th>
                <th className="p-2 border-r">RATE</th>
                <th className="p-2">AMOUNT</th>
              </tr>
            </thead>
            <tbody>
              {savedInvoice.items.map((it, index) => {
                const name =
                  it.type === "Product" ? it.itemName : it.serviceName;
                const qty = parseFloat(it.qty || 0);
                const rate = parseFloat(it.salesPrice || 0);
                const amount = qty * rate;
                return (
                  <tr key={index} className="border-b">
                    <td className="p-2 border-r text-center">{index + 1}</td>
                    <td className="p-2 border-r">{name}</td>
                    <td className="p-2 border-r text-center">
                      {qty} {it.measuringUnit || ""}
                    </td>
                    <td className="p-2 border-r text-center">{rate}</td>
                    <td className="p-2 text-right">{amount.toFixed(2)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {/* TOTAL / RECEIVED AMOUNT */}
          <div className="flex justify-end">
            <table className="text-sm border">
              <tbody>
                <tr className="border-b">
                  <td className="px-2 py-1 font-semibold border-r">TOTAL</td>
                  <td className="px-2 py-1 border-r">
                    {savedInvoice.items.length}
                  </td>
                  <td className="px-2 py-1 text-right">
                    ₹ {savedInvoice.grandTotal}
                  </td>
                </tr>
                <tr>
                  <td className="px-2 py-1 font-semibold border-r">
                    RECEIVED AMOUNT
                  </td>
                  <td colSpan={2} className="px-2 py-1 text-right">
                    ₹ {savedInvoice.receivedAmount || 0}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Amount in Words */}
          <div className="mt-4 text-sm">
            <p className="font-semibold">Total Amount (in words)</p>
            <p className="italic">Zero Rupees</p>
          </div>

          {/* Terms & Conditions */}
          <div className="mt-4 text-sm">
            <h4 className="font-semibold">Terms and Conditions</h4>
            <p>1. Goods once sold will not be taken back or exchanged</p>
            <p>
              2. All disputes are subject to [ENTER_YOUR_CITY_NAME] jurisdiction
              only
            </p>
          </div>

          {/* Authorized Signatory */}
          <div className="mt-4 flex justify-end">
            <div className="text-right text-sm">
              <p className="font-semibold">
                Authorized Signatory For Business Name
              </p>
              <div className="border border-dashed w-32 h-16 mt-2" />
            </div>
          </div>
        </div>

        {/* DELETE CONFIRMATION MODAL */}
        {showDeleteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded shadow-lg w-full max-w-sm">
              <h3 className="text-lg font-semibold mb-2">
                Are you sure you want to delete this Sales Invoice?
              </h3>
              <p className="text-sm text-gray-500 mb-4">
                Once deleted, it cannot be recovered.
              </p>
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="px-4 py-2 bg-gray-100 rounded text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmDelete}
                  className="px-4 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                >
                  Yes, Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </>
    );
  }

  // ------------------------------------------------------------------
  // 9) Otherwise, show the normal create-invoice form
  // ------------------------------------------------------------------
  return (
    <>
      <div className="h-screen flex flex-col overflow-hidden bg-gray-100 ">
        {/* Top Bar */}
        <div className="flex items-center justify-between p-4 bg-white border-b flex-none">
          <button
            onClick={handleSettings}
            className="px-4 py-2 border rounded hover:bg-gray-50"
          >
            Settings
          </button>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleSaveAndNew}
              className="px-4 py-2 border rounded hover:bg-gray-50"
            >
              Save &amp; New
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Save
            </button>
          </div>
        </div>

        {/* Main Create-Invoice Form */}
        <div className="flex-1 overflow-y-auto p-4">
          {/* TOP ROW: BILL TO, SHIP TO, SALES INVOICE DETAILS */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
            {/* Bill To */}
            <div className="bg-white border rounded p-4 space-y-2">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold text-sm">Bill To</h2>
                <button
                  onClick={() => setShowPartyDropdown(true)}
                  className="px-2 py-1 text-sm border rounded hover:bg-gray-50"
                >
                  Change Party
                </button>
              </div>
              <p className="text-sm font-medium">
                {selectedParty ? selectedParty.party_name : "[Party Name]"}
              </p>
              <p className="text-sm text-gray-600">
                Phone Number:{" "}
                {selectedParty?.mobile_number ? selectedParty.mobile_number : "[xxxxxxx]"}
              </p>
              {showPartyDropdown && (
                <div className="mt-2 bg-white border border-gray-200 rounded shadow-lg p-2 relative z-10">
                  <input
                    type="text"
                    placeholder="Search party by name or number"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded mb-2 text-sm"
                  />
                  {filteredParties.map((p) => (
                    <div
                      key={p.id}
                      onClick={() => handleSelectParty(p)}
                      className="flex justify-between p-2 hover:bg-gray-100 cursor-pointer text-sm"
                    >
                      <span>{p.party_name}</span>
                      <span className="text-gray-500">
                        ₹ {Math.abs(p.opening_balance_amount) || 0}{" "}
                        {p.opening_balance === 'to_'? (
                          <span className="text-green-600">&#8595;</span>
                        ) : (
                          <span className="text-red-600">&#8593;</span>
                        )}
                      </span>
                    </div>
                  ))}
                  <div
                    onClick={() => navigate("/createparty")}
                    className="p-2 text-blue-500 text-sm font-medium border-t border-gray-200 hover:bg-gray-50 cursor-pointer"
                  >
                    + Create Party
                  </div>
                </div>
              )}
            </div>

            {/* Ship To */}
            <div className="bg-white border rounded p-4 space-y-2">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold text-sm">Ship To</h2>
                <button
                  onClick={handleChangeShippingAddress}
                  className="px-2 py-1 text-sm border rounded hover:bg-gray-50"
                >
                  Change Shipping Address
                </button>
              </div>
              <p className="text-sm font-medium">
                {selectedParty ? selectedParty.name : "[Shipping Name]"}
              </p>
              <p className="text-sm text-gray-600">
                Phone Number:{" "}
                {selectedParty?.mobile ? selectedParty.mobile : "[xxxxxxx]"}
              </p>
              <p className="text-sm text-gray-500">{renderShippingAddress()}</p>
            </div>

            {/* Sales Invoice Details */}
            <div className="bg-white border rounded p-4 space-y-3">
              <div className="grid grid-cols-2 gap-2 items-center">
                <label className="text-sm text-gray-600">Sales Invoice No</label>
                <input
                  type="text"
                  placeholder="ex: 4"
                  value={invoiceNumber}
                  onChange={(e) => setInvoiceNumber(e.target.value)}
                  className="border rounded p-1 text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-2 items-center">
                <label className="text-sm text-gray-600">Sales Invoice Date</label>
                <input
                  type="date"
                  value={invoiceDate}
                  onChange={(e) => setInvoiceDate(e.target.value)}
                  className="border rounded p-1 text-sm"
                />
              </div>
              <div className="grid grid-cols-3 gap-2 items-center">
                <label className="col-span-2 text-sm text-gray-600">
                  Payment Terms
                </label>
                <div className="flex items-center space-x-1">
                  <input
                    type="number"
                    placeholder="30"
                    className="border rounded p-1 text-sm w-16"
                  />
                  <span className="text-sm text-gray-600">days</span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 items-center">
                <label className="text-sm text-gray-600">Due Date</label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="border rounded p-1 text-sm"
                />
              </div>
            </div>
          </div>

          {/* ITEMS TABLE */}
          <div className="bg-white border rounded p-4">
            <div className="flex items-center justify-between pb-2 border-b mb-2">
              <div className="text-sm font-semibold text-gray-700">
                <span>ITEMS / SERVICES</span>
              </div>
              <button
                onClick={handleScanBarcode}
                className="px-2 py-1 border rounded text-sm hover:bg-gray-50"
              >
                Scan Barcode
              </button>
            </div>
            <div className="hidden md:grid grid-cols-8 gap-2 text-xs font-medium text-gray-500 border-b pb-2">
              <div className="text-center">NO</div>
              <div className="col-span-2">ITEMS / SERVICES</div>
              <div className="text-center">HSN / SAC</div>
              <div className="text-center">QTY</div>
              <div className="text-center">PRICE (ITEM)</div>
              <div className="text-center">DISCOUNT</div>
              <div className="text-center">TAX</div>
              <div className="text-center">AMOUNT (₹)</div>
            </div>
            {invoiceItems.length === 0 ? (
              <div className="my-4 text-center text-gray-500">
                No items added yet
              </div>
            ) : (
              invoiceItems.map((item, idx) => {
                const itemName =
                  item.type === "Product" ? item.itemName : item.serviceName;
                const hsn = item.type === "Product" ? item.hsnCode || "-" : "SAC";
                const qty = parseFloat(item.qty || 0);
                const price = parseFloat(item.salesPrice || 0);
                const discount = parseFloat(item.discount || 0);
                const numericTaxRate = parseFloat(item.tax || 0);
                const lineSubtotal = qty * price;
                const lineDiscount = (lineSubtotal * discount) / 100;
                const lineTax = (lineSubtotal * numericTaxRate) / 100;
                const lineTotal = lineSubtotal + lineTax - lineDiscount;
                return (
                  <div
                    key={idx}
                    className="grid grid-cols-8 gap-2 text-sm items-center border-b py-2"
                  >
                    <div className="text-center">{idx + 1}</div>
                    <div className="col-span-2">
                      <div className="font-medium">{itemName}</div>
                      <div className="text-xs text-gray-400">
                        {item.category}
                      </div>
                    </div>
                    <div className="text-center">{hsn}</div>
                    <div className="text-center">
                      <input
                        type="number"
                        className="border rounded p-1 w-16 text-sm text-right"
                        value={item.qty || ""}
                        onChange={(e) => handleQtyChange(idx, e.target.value)}
                      />
                    </div>
                    <div className="text-center">
                      <input
                        type="number"
                        className="border rounded p-1 w-16 text-sm text-right"
                        value={item.salesPrice || ""}
                        onChange={(e) => handlePriceChange(idx, e.target.value)}
                      />
                    </div>
                    <div className="text-center">
                      <input
                        type="number"
                        className="border rounded p-1 w-12 text-sm text-right"
                        value={item.discount || ""}
                        onChange={(e) => handleDiscountChange(idx, e.target.value)}
                        placeholder="%"
                      />
                    </div>
                    <div className="text-center">
                      <select
                        className="border rounded p-1 text-sm"
                        value={
                          taxOptions.find((o) => o.value === item.tax)?.label ||
                          "None"
                        }
                        onChange={(e) => handleTaxChange(idx, e.target.value)}
                      >
                        {taxOptions.map((o) => (
                          <option key={o.label} value={o.label}>
                            {o.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="text-center">{lineTotal.toFixed(2)}</div>
                    <div className="col-span-8 flex justify-end">
                      <button
                        onClick={() => handleRemoveInvoiceItem(idx)}
                        className="text-xs text-red-500"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                );
              })
            )}
            <div
              onClick={handleAddItem}
              className="border-dashed border-2 border-blue-400 rounded text-center py-6 my-4 text-sm text-blue-500 cursor-pointer"
            >
              + Add Item
            </div>
            <div className="mt-4 flex justify-end">
              <table className="text-right text-sm">
                <tbody>
                  <tr>
                    <td className="px-4 py-1">Subtotal</td>
                    <td className="px-4 py-1">₹{subtotal.toFixed(2)}</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-1">Discount</td>
                    <td className="px-4 py-1">₹{discountTotal.toFixed(2)}</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-1">Tax</td>
                    <td className="px-4 py-1">₹{taxTotal.toFixed(2)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* 2-COLUMN LAYOUT */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            {/* LEFT COLUMN: Notes, Terms, New Account */}
            <div className="space-y-2">
              {!showNotes && (
                <button
                  onClick={() => setShowNotes(true)}
                  className="text-blue-500 text-sm font-medium"
                >
                  + Add Notes
                </button>
              )}
              {showNotes && (
                <div className="bg-white border rounded p-4 space-y-2">
                  <div className="flex justify-between items-center">
                    <label className="text-sm font-medium">Notes</label>
                    <button
                      onClick={() => setShowNotes(false)}
                      className="text-sm text-gray-400 hover:text-gray-600"
                    >
                      &times;
                    </button>
                  </div>
                  <textarea
                    className="w-full border rounded p-2 text-sm"
                    placeholder="Enter your notes"
                  />
                </div>
              )}

              {!showTerms && (
                <button
                  onClick={() => setShowTerms(true)}
                  className="text-blue-500 text-sm font-medium"
                >
                  + Add Terms and Conditions
                </button>
              )}
              {showTerms && (
                <div className="bg-white border rounded p-4 space-y-2">
                  <div className="flex justify-between items-center">
                    <label className="text-sm font-medium">
                      Terms and Conditions
                    </label>
                    <button
                      onClick={() => setShowTerms(false)}
                      className="text-sm text-gray-400 hover:text-gray-600"
                    >
                      &times;
                    </button>
                  </div>
                  <textarea
                    className="w-full border rounded p-2 text-sm"
                    placeholder="Enter your terms and conditions"
                  />
                </div>
              )}

              <button
                onClick={() => setShowNewAccountModal(true)}
                className="text-blue-500 text-sm font-medium"
              >
                + Add New Account
              </button>
            </div>

            {/* RIGHT COLUMN: Additional Charges, Discount, Payment, etc. */}
            <div className="space-y-4 text-sm">
              {showAdditionalCharge ? (
                <div className="relative border p-2 rounded space-y-2">
                  <button
                    className="absolute -top-3 -right-4 text-gray-400 hover:text-gray-600 text-xl"
                    onClick={() => {
                      setShowAdditionalCharge(false);
                      setAdditionalCharge(0);
                      setAdditionalChargeTaxRate(0);
                    }}
                  >
                    &times;
                  </button>
                  <label className="block text-sm font-medium">
                    Additional Charge
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      placeholder="Description (e.g. Transport Charge)"
                      className="border rounded p-2 text-sm flex-1"
                    />
                    <input
                      type="number"
                      placeholder="₹ 0"
                      value={additionalCharge}
                      onChange={(e) => setAdditionalCharge(e.target.value)}
                      className="border rounded p-2 text-sm w-24 text-right"
                    />
                    <select
                      value={additionalChargeTaxRate}
                      onChange={(e) => setAdditionalChargeTaxRate(e.target.value)}
                      className="border rounded p-2 text-sm"
                    >
                      <option value={0}>No Tax Applicable</option>
                      <option value={5}>GST @ 5%</option>
                      <option value={12}>GST @ 12%</option>
                      <option value={18}>GST @ 18%</option>
                      <option value={28}>GST @ 28%</option>
                    </select>
                  </div>
                </div>
              ) : (
                <button
                  className="text-blue-500 font-medium"
                  onClick={() => setShowAdditionalCharge(true)}
                >
                  + Add Additional Charges
                </button>
              )}

              <div className="flex justify-between items-center">
                <span>Taxable Amount</span>
                <span>
                  ₹ {Math.max(0, subtotal + taxTotal - discountTotal).toFixed(2)}
                </span>
              </div>

              {showDiscount ? (
                <div className="relative border p-2 rounded space-y-2">
                  <button
                    className="absolute -top-3 -right-4 text-gray-400 hover:text-gray-600 text-xl"
                    onClick={() => {
                      setShowDiscount(false);
                      setDiscountAfterTax(0);
                    }}
                  >
                    &times;
                  </button>
                  <label className="block text-sm font-medium">
                    Discount After Tax
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      placeholder={discountAfterTaxIsPercent ? "% 0" : "₹ 0"}
                      value={discountAfterTax}
                      onChange={(e) => setDiscountAfterTax(e.target.value)}
                      className="border rounded p-2 text-sm w-24 text-right"
                    />
                    <select
                      className="border rounded p-1 text-sm"
                      value={discountAfterTaxIsPercent ? "%" : "₹"}
                      onChange={(e) =>
                        setDiscountAfterTaxIsPercent(e.target.value === "%")
                      }
                    >
                      <option value="%">%</option>
                      <option value="₹">₹</option>
                    </select>
                  </div>
                </div>
              ) : (
                <button
                  className="text-blue-500 font-medium"
                  onClick={() => setShowDiscount(true)}
                >
                  + Add Discount
                </button>
              )}

              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={autoRoundOff}
                    onChange={(e) => setAutoRoundOff(e.target.checked)}
                  />
                  Auto Round Off
                </label>
                {autoRoundOff && (
                  <div className="flex items-center space-x-2">
                    <span>Add</span>
                    <input
                      type="number"
                      placeholder="0"
                      value={roundOffValue}
                      onChange={(e) => setRoundOffValue(e.target.value)}
                      className="w-16 border rounded p-1 text-sm text-right"
                    />
                  </div>
                )}
              </div>

              <div className="flex justify-between items-center text-base">
                <span className="font-semibold">Total Amount</span>
                <span className="font-bold">₹ {grandTotal.toFixed(2)}</span>
              </div>

              {exceedsCreditLimit && (
                <div className="text-red-600 text-sm">
                  Warning! Invoice amount exceeds the set credit limit of ₹
                  {selectedParty?.creditLimit || 0} for this party
                </div>
              )}

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="fullyPaid"
                  className="mr-1"
                  checked={markAsFullyPaid}
                  onChange={(e) => setMarkAsFullyPaid(e.target.checked)}
                />
                <label htmlFor="fullyPaid">Mark as fully paid</label>
              </div>

              <div className="flex justify-between items-center">
                <span>Balance Amount</span>
                <span
                  className={`font-semibold ${
                    balanceAmount === 0 ? "text-green-600" : ""
                  }`}
                >
                  ₹ {balanceAmount.toFixed(2)}
                </span>
              </div>

              <div className="pt-2 text-sm text-gray-500 border-t">
                Authorized signatory for <strong>Business Name</strong>
                <div className="mt-2 flex justify-end">
                  <div className="border border-dashed rounded w-32 h-20" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal for Add Bank Account */}
      {showNewAccountModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg w-full max-w-xl space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Add Bank Account</h3>
              <button
                onClick={() => setShowNewAccountModal(false)}
                className="text-2xl text-gray-400 hover:text-gray-600"
              >
                &times;
              </button>
            </div>
            <div>
              <label className="text-sm font-medium block mb-1">
                Account Name*
              </label>
              <input
                type="text"
                placeholder="ex: Personal Account"
                value={accountName}
                onChange={(e) => setAccountName(e.target.value)}
                className="w-full border rounded p-2 text-sm"
              />
            </div>
            <div className="flex flex-col md:flex-row md:space-x-4">
              <div className="flex-1">
                <label className="text-sm font-medium block mb-1">
                  Opening Balance
                </label>
                <input
                  type="text"
                  placeholder="ex: ₹10,000"
                  value={openingBalance}
                  onChange={(e) => setOpeningBalance(e.target.value)}
                  className="w-full border rounded p-2 text-sm"
                />
              </div>
              <div className="flex-1">
                <label className="text-sm font-medium block mb-1">
                  As of Date
                </label>
                <input
                  type="date"
                  value={asOfDate}
                  onChange={(e) => setAsOfDate(e.target.value)}
                  className="w-full border rounded p-2 text-sm"
                />
              </div>
            </div>
            <h4 className="text-md font-semibold mt-2">Add Bank Details</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium block mb-1">
                  Bank Account Number*
                </label>
                <input
                  type="text"
                  placeholder="ex: 123456789157950"
                  value={bankAccountNumber}
                  onChange={(e) => setBankAccountNumber(e.target.value)}
                  className="w-full border rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">
                  Re-Enter Bank Account Number*
                </label>
                <input
                  type="text"
                  placeholder="ex: 123456789157950"
                  value={reEnterBankAccountNumber}
                  onChange={(e) => setReEnterBankAccountNumber(e.target.value)}
                  className="w-full border rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">
                  IFSC Code*
                </label>
                <input
                  type="text"
                  placeholder="ex: HDFC0001234"
                  value={ifscCode}
                  onChange={(e) => setIfscCode(e.target.value)}
                  className="w-full border rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">
                  Bank & Branch Name
                </label>
                <input
                  type="text"
                  placeholder="ex: HDFC, Old Madras"
                  value={bankBranch}
                  onChange={(e) => setBankBranch(e.target.value)}
                  className="w-full border rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">
                  Account Holders Name*
                </label>
                <input
                  type="text"
                  placeholder="ex: Elisa wolf"
                  value={accountHolderName}
                  onChange={(e) => setAccountHolderName(e.target.value)}
                  className="w-full border rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">UPI ID</label>
                <input
                  type="text"
                  placeholder="ex: elisa@okhdfc"
                  value={upiId}
                  onChange={(e) => setUpiId(e.target.value)}
                  className="w-full border rounded p-2 text-sm"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-2 mt-4">
              <button
                onClick={() => setShowNewAccountModal(false)}
                className="px-4 py-2 bg-gray-300 rounded text-sm"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  alert("Submitted new bank account");
                  setShowNewAccountModal(false);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Change Shipping Address */}
      {showChangeShippingModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Change Shipping Address</h3>
              <button
                onClick={() => setShowChangeShippingModal(false)}
                className="text-xl text-gray-400 hover:text-gray-600"
              >
                &times;
              </button>
            </div>
            {shippingAddresses.length === 0 ? (
              <div className="p-4 text-gray-500 text-sm">
                No Shipping Addresses found.
              </div>
            ) : (
              <div className="space-y-2 mb-4">
                {shippingAddresses.map((addr) => (
                  <div
                    key={addr.id}
                    className="p-2 border rounded flex items-center justify-between"
                  >
                    <div className="text-sm">
                      <div className="font-medium">
                        {addr.name || "Untitled"}
                      </div>
                      <div className="text-gray-600 text-xs">
                        {addr.street ? addr.street : "No Address"}
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEditShippingAddress(addr)}
                        className="text-xs text-blue-600 border rounded px-2 py-1"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleSelectShippingAddress(addr)}
                        className="text-xs text-blue-600 border rounded px-2 py-1"
                      >
                        Select
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <button
              onClick={handleAddNewShippingAddress}
              className="text-sm text-blue-600 font-medium mb-4"
            >
              + Add New Shipping Address
            </button>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowChangeShippingModal(false)}
                className="px-4 py-2 bg-gray-300 rounded text-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleDoneShipping}
                className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Edit/Add Shipping Address */}
      {showEditShippingModal && editingAddress && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg w-full max-w-md space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">
                {editingAddress.id ? "Edit" : "Add"} Shipping Address
              </h3>
              <button
                onClick={() => setShowEditShippingModal(false)}
                className="text-2xl text-gray-400 hover:text-gray-600"
              >
                &times;
              </button>
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">Shipping Name*</label>
              <input
                type="text"
                placeholder="Business Name"
                value={editingAddress.name || ""}
                onChange={(e) =>
                  setEditingAddress({ ...editingAddress, name: e.target.value })
                }
                className="w-full border rounded p-2 text-sm"
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">Street Address*</label>
              <input
                type="text"
                placeholder="Enter Street Address"
                value={editingAddress.street || ""}
                onChange={(e) =>
                  setEditingAddress({
                    ...editingAddress,
                    street: e.target.value,
                  })
                }
                className="w-full border rounded p-2 text-sm"
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="flex flex-col">
                <label className="text-sm font-medium">State</label>
                <select
                  value={editingAddress.state || ""}
                  onChange={(e) =>
                    setEditingAddress({
                      ...editingAddress,
                      state: e.target.value,
                    })
                  }
                  className="border rounded p-2 text-sm"
                >
                  <option value="">Select State</option>
                  {indianStates.map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex flex-col">
                <label className="text-sm font-medium">Pincode</label>
                <input
                  type="text"
                  placeholder="Enter pincode"
                  value={editingAddress.pincode || ""}
                  onChange={handlePincodeChange}
                  className="border rounded p-2 text-sm"
                />
              </div>
            </div>
            <div className="flex flex-col">
              <label className="text-sm font-medium">City</label>
              <input
                type="text"
                placeholder="Enter City"
                value={editingAddress.city || ""}
                onChange={(e) =>
                  setEditingAddress({
                    ...editingAddress,
                    city: e.target.value,
                  })
                }
                className="border rounded p-2 text-sm"
              />
            </div>
            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowEditShippingModal(false)}
                className="px-4 py-2 bg-gray-300 rounded text-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveShippingAddress}
                className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Add Items */}
      {showAddItemsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded shadow-lg w-full max-w-4xl p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Add Items</h3>
              <button
                onClick={handleCloseAddItemsModal}
                className="text-2xl text-gray-400 hover:text-gray-600"
              >
                &times;
              </button>
            </div>
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-4 gap-2">
              <div className="flex items-center gap-2 flex-1">
                <input
                  type="text"
                  placeholder="Search Items"
                  value={itemSearchTerm}
                  onChange={(e) => setItemSearchTerm(e.target.value)}
                  className="border rounded p-2 text-sm w-full md:w-1/2"
                />
                <select
                  value={itemCategoryFilter}
                  onChange={(e) => setItemCategoryFilter(e.target.value)}
                  className="border rounded p-2 text-sm"
                >
                  <option value="Select Category">Select Category</option>
                  {itemCategories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
              <button
                onClick={handleCreateNewItem}
                className="text-blue-600 font-medium text-sm"
              >
                + Create New Item
              </button>
            </div>
            <div className="overflow-auto max-h-80 border rounded">
              <table className="min-w-full text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="p-2 text-left">Name</th>
                    <th className="p-2 text-left">Item Code</th>
                    <th className="p-2 text-left">Sales Price</th>
                    <th className="p-2 text-left">Purchase Price</th>
                    <th className="p-2 text-left">Current Stock</th>
                    <th className="p-2 text-left">Quantity</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredModalItems.length === 0 ? (
                    <tr>
                      <td
                        colSpan="6"
                        className="text-center py-4 text-gray-500"
                      >
                        No items found
                      </td>
                    </tr>
                  ) : (
                    filteredModalItems.map((it, index) => {
                      const name =
                        it.type === "Product" ? it.itemName : it.serviceName;
                      const code =
                        it.type === "Product"
                          ? it.itemCode || "-"
                          : it.serviceCode || "SRV";
                      const sales = it.salesPrice || 0;
                      const purchase = it.purchasePrice || 0;
                      const stock =
                        it.type === "Product" && it.openingStock
                          ? `${it.openingStock} ${it.measuringUnit || ""}`
                          : it.type === "Product"
                          ? "0"
                          : "-";
                      return (
                        <tr key={index} className="border-b">
                          <td className="p-2">{name}</td>
                          <td className="p-2">{code}</td>
                          <td className="p-2">₹ {sales}</td>
                          <td className="p-2">₹ {purchase}</td>
                          <td className="p-2">
                            {parseFloat(it.openingStock || 0) <= 0 ? (
                              <span className="text-red-500">
                                {stock} (Insufficient Stock)
                              </span>
                            ) : (
                              <>{stock}</>
                            )}
                          </td>
                          <td className="p-2">
                            <input
                              type="number"
                              className="border rounded w-16 p-1 text-right"
                              value={modalQuantities[index] || ""}
                              onChange={(e) =>
                                handleChangeModalQuantity(index, e.target.value)
                              }
                            />
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
            <div className="mt-4 flex justify-between items-center">
              <div className="text-sm">
                {
                  Object.values(modalQuantities).filter((q) => parseFloat(q) > 0)
                    .length
                }{" "}
                Items Selected
              </div>
              <div className="space-x-2">
                <button
                  onClick={handleCloseAddItemsModal}
                  className="px-4 py-2 bg-gray-300 rounded text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDoneAddingItems}
                  className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default CreateSalesInvoice;
