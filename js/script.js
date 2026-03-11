// ---------- SESSION KEY ----------
const SESSION_KEY = "ars_loggedInUser";

// ---------- HELPERS ----------
function getUsers(){
  return JSON.parse(localStorage.getItem("ars_users") || "[]");
}
function saveUsers(users){
  localStorage.setItem("ars_users", JSON.stringify(users));
}

function requireLogin(){
  const u = localStorage.getItem(SESSION_KEY);
  if(!u){
    alert("Please login first!");
    window.location.href = "login.html";
  }
}

function setNavUser(){
  const navUser = document.getElementById("navUser");
  if(!navUser) return;
  const u = localStorage.getItem(SESSION_KEY);
  navUser.innerText = u ? u : "Guest";
}

async function logout(){
  try {
    await fetch('/api/logout', {
      method: 'POST',
      credentials: 'include'
    });
  } catch (error) {
    console.error("Logout error:", error);
  }
  localStorage.removeItem(SESSION_KEY);
  alert("Logged out successfully!");
  window.location.href = "login.html";
}

// ---------- REGISTER ----------
async function registerUser(e){
  e.preventDefault();

  const name = document.getElementById("regName").value.trim();
  const email = document.getElementById("regEmail").value.trim().toLowerCase();
  const pass = document.getElementById("regPass").value.trim();

  if(!name || !email || !pass){
    alert("Please fill all fields!");
    return;
  }

  try {
    const response = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password: pass })
    });
    const data = await response.json();
    if (response.ok) {
      alert("Registration successful! Please login.");
      window.location.href = "login.html";
    } else {
      alert(data.error || "Registration failed");
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

// ---------- LOGIN ----------
async function loginUser(e){
  e.preventDefault();

  const email = document.getElementById("loginEmail").value.trim().toLowerCase();
  const pass = document.getElementById("loginPass").value.trim();

  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password: pass })
    });
    const data = await response.json();
    if (response.ok) {
      localStorage.setItem(SESSION_KEY, email);
      alert("Login successful!");
      window.location.href = "index.html";
    } else {
      alert(data.error || "Login failed");
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

// ---------- HOME SEARCH ----------
async function searchFlights(e){
  e.preventDefault();

  requireLogin();

  const from = document.getElementById("fromCity").value;
  const to = document.getElementById("toCity").value;
  const date = document.getElementById("travelDate").value;
  const seats = parseInt(document.getElementById("seatCount").value || "1");

  if(from === to){
    alert("From and To cannot be same!");
    return;
  }

  if(!date){
    alert("Please select a travel date!");
    return;
  }

  try {
    const response = await fetch('/api/flights');
    const flights = await response.json();

    if (!response.ok) {
      alert("Failed to load flights");
      return;
    }

    // Filter flights based on search criteria
    const availableFlights = flights.filter(f =>
      f.from.toLowerCase() === from.toLowerCase() &&
      f.to.toLowerCase() === to.toLowerCase() &&
      f.date === date
    );

    displayFlights(availableFlights, seats);

    // Store search data for booking
    const bookingSearch = {from, to, date, seats};
    localStorage.setItem("ars_search", JSON.stringify(bookingSearch));

  } catch (error) {
    alert("Error searching flights: " + error.message);
  }
}

function displayFlights(flights, seats) {
  const resultsDiv = document.getElementById("flightResults");
  const flightsList = document.getElementById("flightsList");

  if (flights.length === 0) {
    flightsList.innerHTML = "<p class='small-text'>No flights available for selected route and date.</p>";
    resultsDiv.style.display = "block";
    return;
  }

  let html = "";
  flights.forEach(flight => {
    const totalPrice = flight.price * seats;
    html += `
      <div class="flight-card">
        <div class="flight-header">
          <div class="airline-info">
            <h4>${flight.airline} - ${flight.flight_number}</h4>
            <span class="flight-class">${flight.class}</span>
          </div>
          <div class="flight-times">
            <div class="time">${flight.departure}</div>
            <div class="duration">${flight.duration}</div>
            <div class="time">${flight.arrival}</div>
          </div>
        </div>
        <div class="flight-route">
          <span>${flight.from} → ${flight.to}</span>
          <span class="date">${flight.date}</span>
        </div>
        <div class="flight-footer">
          <div class="price">₹${totalPrice} <small>for ${seats} passenger${seats > 1 ? 's' : ''}</small></div>
          <button class="btn-primary" onclick="selectFlight('${flight.flight_number}', ${totalPrice})">Select Flight</button>
        </div>
      </div>
    `;
  });

  flightsList.innerHTML = html;
  resultsDiv.style.display = "block";
  resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

function selectFlight(flightNumber, totalPrice) {
  // Store selected flight info
  const search = JSON.parse(localStorage.getItem("ars_search") || "{}");
  const selectedFlight = {
    flightNumber,
    totalPrice,
    ...search
  };
  localStorage.setItem("ars_selectedFlight", JSON.stringify(selectedFlight));

  // Proceed to reservation
  window.location.href = "reservation.html";
}

// ---------- RESERVATION ----------
function loadReservation(){
  requireLogin();

  const search = JSON.parse(localStorage.getItem("ars_search") || "{}");
  const selectedFlight = JSON.parse(localStorage.getItem("ars_selectedFlight") || "{}");

  if(!search.from){
    alert("Please search flights first!");
    window.location.href = "index.html";
    return;
  }

  let routeText = `Route: ${search.from} → ${search.to} | Date: ${search.date} | Passengers: ${search.seats}`;
  if(selectedFlight.flightNumber){
    routeText += ` | Flight: ${selectedFlight.flightNumber}`;
  }

  document.getElementById("routeText").innerText = routeText;
  document.getElementById("seatCountRes").value = search.seats;

  calcFare();
}

function calcFare(){
  const selectedFlight = JSON.parse(localStorage.getItem("ars_selectedFlight") || "{}");
  const cls = document.getElementById("travelClass").value;
  const seats = parseInt(document.getElementById("seatCountRes").value || "1");

  let basePerSeat;
  if(selectedFlight.totalPrice){
    // Use selected flight price
    basePerSeat = selectedFlight.totalPrice / seats;
  } else {
    // Fallback to default pricing
    basePerSeat = 2500;
    if(cls === "Business") basePerSeat = 5200;
    if(cls === "First") basePerSeat = 8200;
  }

  const base = basePerSeat * seats;
  const tax = Math.round(base * 0.12);
  const total = base + tax;

  document.getElementById("baseFare").innerText = "₹" + base;
  document.getElementById("taxFare").innerText = "₹" + tax;
  document.getElementById("totalFare").innerText = "₹" + total;

  localStorage.setItem("ars_fare", JSON.stringify({base,tax,total,cls,seats}));
}

async function proceedTicket(){
  requireLogin();

  const pname = document.getElementById("passengerName").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const aadhar = document.getElementById("aadharNumber").value.trim();
  const addr = document.getElementById("address").value.trim();

  if(!pname || !phone || !aadhar || !addr){
    alert("Please fill all passenger details!");
    return;
  }

  // Validate Aadhar format
  if(!/^\d{12}$/.test(aadhar)){
    alert("Please enter a valid 12-digit Aadhar number!");
    return;
  }

  const search = JSON.parse(localStorage.getItem("ars_search") || "{}");
  const fare = JSON.parse(localStorage.getItem("ars_fare") || "{}");

  const bookingData = {
    passenger_name: pname,
    phone,
    aadhar_number: aadhar,
    address: addr,
    from: search.from,
    to: search.to,
    date: search.date,
    seats: fare.seats,
    class: fare.cls,
    base: fare.base,
    tax: fare.tax,
    total: fare.total
  };

  try {
    const response = await fetch('/api/book', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(bookingData)
    });
    const data = await response.json();
    if (response.ok) {
      localStorage.setItem("ars_currentBooking", JSON.stringify({
        ticketId: data.ticket_id,
        user: localStorage.getItem(SESSION_KEY),
        passengerName: pname,
        phone,
        aadharNumber: aadhar,
        address: addr,
        from: search.from,
        to: search.to,
        date: search.date,
        seats: fare.seats,
        class: fare.cls,
        base: fare.base,
        tax: fare.tax,
        total: fare.total,
        bookedAt: new Date().toLocaleString()
      }));
      window.location.href = "confirm.html";
    } else {
      alert(data.error || "Booking failed");
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

// ---------- CONFIRM ----------
function loadConfirm(){
  requireLogin();

  const booking = JSON.parse(localStorage.getItem("ars_currentBooking") || "{}");
  if(!booking.ticketId){
    alert("No ticket found!");
    window.location.href = "index.html";
    return;
  }

  document.getElementById("tId").innerText = booking.ticketId;
  document.getElementById("tUser").innerText = booking.user;
  document.getElementById("tName").innerText = booking.passengerName;
  document.getElementById("tPhone").innerText = booking.phone;
  document.getElementById("tAadhar").innerText = booking.aadharNumber;
  document.getElementById("tRoute").innerText = booking.from + " → " + booking.to;
  document.getElementById("tDate").innerText = booking.date;
  document.getElementById("tClass").innerText = booking.class;
  document.getElementById("tSeats").innerText = booking.seats;
  document.getElementById("tFare").innerText = "₹" + booking.total;
  document.getElementById("tBooked").innerText = booking.bookedAt;
}

function printTicketPDF(){
  // Browser will open Print dialog -> choose "Save as PDF"
  window.print();
}

// ---------- MY BOOKINGS ----------
async function loadMyBookings(){
  requireLogin();

  try {
    const response = await fetch('/api/bookings', {
      credentials: 'include'
    });
    const list = await response.json();
    if (!response.ok) {
      alert(list.error || "Failed to load bookings");
      return;
    }

    const box = document.getElementById("bookingsList");
    box.innerHTML = "";

    if(list.length === 0){
      box.innerHTML = "<p class='small-text'>No bookings found.</p>";
      return;
    }

    list.forEach(b=>{
      const div = document.createElement("div");
      div.className = "ticket-box fade-in";
      div.style.marginBottom = "12px";

      div.innerHTML = `
        <div class="ticket-grid">
          <div><b>Ticket ID:</b> ${b.ticket_id}</div>
          <div><b>Booked At:</b> ${b.booked_at}</div>
          <div><b>Passenger:</b> ${b.passenger_name}</div>
          <div><b>Phone:</b> ${b.phone}</div>
          <div><b>Aadhar:</b> ${b.aadhar_number}</div>
          <div><b>Route:</b> ${b.from_city} → ${b.to_city}</div>
          <div><b>Date:</b> ${b.travel_date}</div>
          <div><b>Class:</b> ${b.travel_class}</div>
          <div><b>Passengers:</b> ${b.seats}</div>
          <div class="full"><b>Total Fare:</b> ₹${b.total_fare}</div>
        </div>
        <hr class="soft-line"/>
        <div class="ticket-bottom no-print">
          <button class="btn-outline" onclick="viewTicket('${b.ticket_id}')">View Ticket</button>
          <button class="btn-primary" onclick="cancelTicket('${b.ticket_id}')">Cancel Ticket</button>
        </div>
      `;
      box.appendChild(div);
    });
  } catch (error) {
    alert("Error loading bookings: " + error.message);
  }
}

async function viewTicket(ticketId){
  try {
    const response = await fetch('/api/bookings', {
      credentials: 'include'
    });
    const bookings = await response.json();
    if (!response.ok) {
      alert(bookings.error || "Failed to load bookings");
      return;
    }
    const found = bookings.find(x => x.ticket_id === ticketId);
    if(!found){ alert("Ticket not found!"); return; }
    localStorage.setItem("ars_currentBooking", JSON.stringify({
      ticketId: found.ticket_id,
      user: found.user_email,
      passengerName: found.passenger_name,
      phone: found.phone,
      address: found.address,
      from: found.from_city,
      to: found.to_city,
      date: found.travel_date,
      seats: found.seats,
      class: found.travel_class,
      base: found.base_fare,
      tax: found.tax,
      total: found.total_fare,
      bookedAt: found.booked_at
    }));
    window.location.href = "confirm.html";
  } catch (error) {
    alert("Error: " + error.message);
  }
}

async function cancelTicket(ticketId){
  if(!confirm("Are you sure to cancel this ticket?")) return;

  try {
    const response = await fetch(`/api/booking/${ticketId}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    const data = await response.json();
    if (response.ok) {
      alert("Ticket cancelled successfully!");
      loadMyBookings();
    } else {
      alert(data.error || "Failed to cancel ticket");
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}