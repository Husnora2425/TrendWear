// TrendWear — frontend logikasi (REST API bilan bitta portda ishlaydi)
const $ = (s) => document.querySelector(s);
let CACHE = { customers: [], products: [], orders: [] };

const TITLES = {
  dashboard: ["Boshqaruv paneli", "Biznes ko'rsatkichlarining umumiy ko'rinishi"],
  customers: ["Mijozlar (CRM)", "Mijozlar bazasini boshqarish"],
  products:  ["Ombor (WMS)", "Mahsulotlar va zaxiralarni nazorat qilish"],
  orders:    ["Buyurtmalar (ERP)", "Sotuv buyurtmalarini boshqarish"],
};

// ---- Navigatsiya ----
document.querySelectorAll(".nav-item").forEach(b => {
  b.onclick = () => switchView(b.dataset.view, b);
});
function switchView(view, btn) {
  document.querySelectorAll(".nav-item").forEach(x => x.classList.remove("active"));
  btn.classList.add("active");
  document.querySelectorAll(".view").forEach(v => v.classList.add("hidden"));
  $("#view-" + view).classList.remove("hidden");
  $("#pageTitle").textContent = TITLES[view][0];
  $("#pageSub").textContent = TITLES[view][1];
  if (view === "dashboard") loadDashboard();
  if (view === "customers") loadCustomers();
  if (view === "products") loadProducts();
  if (view === "orders") loadOrders();
}

// ---- API helper ----
async function api(path, opts = {}) {
  const r = await fetch("/api" + path, {
    headers: { "Content-Type": "application/json" }, ...opts
  });
  if (!r.ok) {
    const e = await r.json().catch(() => ({ detail: "Xatolik" }));
    throw new Error(e.detail || "Server xatosi");
  }
  return r.json();
}

function money(n) { return new Intl.NumberFormat('uz-UZ').format(n) + " so'm"; }

function toast(msg, ok = true) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = "toast show " + (ok ? "ok" : "bad");
  setTimeout(() => t.className = "toast", 2600);
}

// ---- Dashboard ----
async function loadDashboard() {
  const s = await api("/stats");
  const cards = [
    { l: "Mijozlar", v: s.customers, t: "CRM", c: "sky" },
    { l: "Mahsulotlar", v: s.products, t: "WMS", c: "rose" },
    { l: "Buyurtmalar", v: s.orders, t: `${s.pending} kutilmoqda`, c: "sky" },
    { l: "Umumiy aylanma", v: money(s.revenue), t: "ERP", c: "rose" },
    { l: "Kam qolgan zaxira", v: s.low_stock, t: "ogohlantirish", c: "rose" },
  ];
  $("#statGrid").innerHTML = cards.map(c => `
    <div class="stat-card ${c.c}">
      <div class="label">${c.l}</div>
      <div class="value">${c.v}</div>
      <span class="tag ${c.c}">${c.t}</span>
    </div>`).join("");

  const orders = await api("/orders");
  CACHE.customers = await api("/customers");
  $("#recentOrders").innerHTML = orders.slice(0, 5).map(o => {
    const cust = CACHE.customers.find(c => c.id === o.customer_id);
    return `<div class="mini-row">
      <div><div class="m-name">#${o.id} · ${cust ? cust.name : "—"}</div>
      <div class="m-meta">${statusBadge(o.status)}</div></div>
      <strong>${money(o.total)}</strong></div>`;
  }).join("") || emptyMini("Hozircha buyurtma yo'q");

  const prods = await api("/products");
  const low = prods.filter(p => p.stock <= p.reorder_level);
  $("#stockAlert").innerHTML = low.map(p => `
    <div class="mini-row"><div><div class="m-name">${p.name}</div>
    <div class="m-meta">${p.sku}</div></div>
    <span class="badge b-low">${p.stock} dona</span></div>`).join("")
    || emptyMini("Barcha mahsulotlar yetarli");
}
function emptyMini(t){return `<div class="mini-row"><span class="m-meta">${t}</span></div>`}
function statusBadge(s) {
  const map = { Pending: "b-pending", Shipped: "b-shipped", Delivered: "b-delivered", Cancelled: "b-cancelled" };
  const uz = { Pending: "Kutilmoqda", Shipped: "Jo'natildi", Delivered: "Yetkazildi", Cancelled: "Bekor" };
  return `<span class="badge ${map[s]}">${uz[s] || s}</span>`;
}

// ---- Customers ----
async function loadCustomers() {
  const data = await api("/customers");
  CACHE.customers = data;
  $("#customersTable").innerHTML = `
    <tr><th>Ism</th><th>Shahar</th><th>Telefon</th><th>Segment</th><th></th></tr>
    ${data.map(c => `<tr>
      <td><strong>${c.name}</strong></td>
      <td>${c.city || "—"}</td>
      <td>${c.phone || "—"}</td>
      <td>${c.segment === "VIP" ? '<span class="badge b-vip">VIP</span>' : c.segment}</td>
      <td><button class="del-btn" onclick="delItem('customers',${c.id})">🗑</button></td>
    </tr>`).join("")}`;
}

// ---- Products ----
async function loadProducts() {
  const data = await api("/products");
  CACHE.products = data;
  $("#productsTable").innerHTML = `
    <tr><th>SKU</th><th>Nomi</th><th>Kategoriya</th><th>Narx</th><th>Zaxira</th><th></th></tr>
    ${data.map(p => `<tr>
      <td><code>${p.sku}</code></td>
      <td><strong>${p.name}</strong></td>
      <td>${p.category || "—"}</td>
      <td>${money(p.price)}</td>
      <td><span class="badge ${p.stock <= p.reorder_level ? 'b-low' : 'b-ok'}">${p.stock} dona</span></td>
      <td><button class="del-btn" onclick="delItem('products',${p.id})">🗑</button></td>
    </tr>`).join("")}`;
}

// ---- Orders ----
async function loadOrders() {
  const data = await api("/orders");
  CACHE.customers = await api("/customers");
  $("#ordersTable").innerHTML = `
    <tr><th>#</th><th>Mijoz</th><th>Summa</th><th>Holat</th><th>Sana</th></tr>
    ${data.map(o => {
      const c = CACHE.customers.find(x => x.id === o.customer_id);
      return `<tr>
        <td><strong>#${o.id}</strong></td>
        <td>${c ? c.name : "—"}</td>
        <td>${money(o.total)}</td>
        <td><select class="sel" onchange="setStatus(${o.id},this.value)">
          ${["Pending","Shipped","Delivered","Cancelled"].map(s =>
            `<option ${s===o.status?'selected':''}>${s}</option>`).join("")}
        </select></td>
        <td>${new Date(o.created_at).toLocaleDateString('uz')}</td>
      </tr>`;
    }).join("")}`;
}
async function setStatus(id, status) {
  try { await api(`/orders/${id}/status?status=${status}`, { method: "PUT" });
    toast("Holat yangilandi"); } catch (e) { toast(e.message, false); }
}

// ---- Delete ----
async function delItem(type, id) {
  if (!confirm("O'chirishni tasdiqlaysizmi?")) return;
  try { await api(`/${type}/${id}`, { method: "DELETE" });
    toast("O'chirildi"); switchView(type, document.querySelector(`[data-view=${type}]`));
  } catch (e) { toast(e.message, false); }
}

// ---- Modal ----
function openModal(type) {
  const body = $("#modalBody");
  if (type === "customer") {
    $("#modalTitle").textContent = "Yangi mijoz";
    body.innerHTML = `
      <label>Ism</label><input id="f_name" placeholder="Kompaniya yoki ism">
      <label>Shahar</label><input id="f_city" placeholder="Toshkent">
      <label>Telefon</label><input id="f_phone" placeholder="+998...">
      <label>Segment</label><select id="f_segment">
        <option>Retail</option><option>Wholesale</option><option>VIP</option></select>
      <button class="add-btn" onclick="saveCustomer()">Saqlash</button>`;
  }
  if (type === "product") {
    $("#modalTitle").textContent = "Yangi mahsulot";
    body.innerHTML = `
      <label>SKU</label><input id="f_sku" placeholder="TW-1006">
      <label>Nomi</label><input id="f_name" placeholder="Mahsulot nomi">
      <label>Kategoriya</label><input id="f_cat" placeholder="Ko'ylak">
      <label>Narx (so'm)</label><input id="f_price" type="number" value="0">
      <label>Zaxira (dona)</label><input id="f_stock" type="number" value="0">
      <button class="add-btn" onclick="saveProduct()">Saqlash</button>`;
  }
  if (type === "order") {
    $("#modalTitle").textContent = "Yangi buyurtma";
    const custOpts = CACHE.customers.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
    const prodOpts = CACHE.products.map(p => `<option value="${p.id}">${p.name} (${p.stock})</option>`).join("");
    body.innerHTML = `
      <label>Mijoz</label><select id="f_cust">${custOpts}</select>
      <label>Mahsulotlar</label>
      <div id="orderLines"></div>
      <button class="link-btn" onclick="addLine()">+ Mahsulot qo'shish</button>
      <button class="add-btn" onclick="saveOrder()">Buyurtmani yaratish</button>`;
    window._prodOpts = prodOpts;
    addLine();
  }
  $("#modalBg").classList.add("open");
}
function addLine() {
  const div = document.createElement("div");
  div.className = "order-line";
  div.innerHTML = `<select class="ol-prod">${window._prodOpts}</select>
    <input class="ol-qty" type="number" value="1" min="1">`;
  $("#orderLines").appendChild(div);
}
function closeModal() { $("#modalBg").classList.remove("open"); }

async function saveCustomer() {
  try {
    await api("/customers", { method: "POST", body: JSON.stringify({
      name: $("#f_name").value, city: $("#f_city").value,
      phone: $("#f_phone").value, segment: $("#f_segment").value }) });
    closeModal(); toast("Mijoz qo'shildi"); loadCustomers();
  } catch (e) { toast(e.message, false); }
}
async function saveProduct() {
  try {
    await api("/products", { method: "POST", body: JSON.stringify({
      sku: $("#f_sku").value, name: $("#f_name").value, category: $("#f_cat").value,
      price: +$("#f_price").value, stock: +$("#f_stock").value }) });
    closeModal(); toast("Mahsulot qo'shildi"); loadProducts();
  } catch (e) { toast(e.message, false); }
}
async function saveOrder() {
  const items = [...document.querySelectorAll(".order-line")].map(l => ({
    product_id: +l.querySelector(".ol-prod").value,
    quantity: +l.querySelector(".ol-qty").value }));
  try {
    await api("/orders", { method: "POST", body: JSON.stringify({
      customer_id: +$("#f_cust").value, items }) });
    closeModal(); toast("Buyurtma yaratildi"); loadOrders();
  } catch (e) { toast(e.message, false); }
}

// ---- Start ----
loadDashboard();
