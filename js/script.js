// ---------- SESSION KEY ----------
const SESSION_KEY = "ars_loggedInUser";

// ---------- HELPERS ----------
function getUsers(){
  return JSON.parse(localStorage.getItem("ars_users") || "[]");
}
function saveUsers(users){
  localStorage.setItem("ars_users", JSON.stringify(users));
}

async function checkServerSession(){
  try {
    const response = await fetch('/api/status', { credentials: 'include' });
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem(SESSION_KEY, data.user);
      return true;
    }
  } catch (error) {
    console.error('Session check failed:', error);
  }
  localStorage.removeItem(SESSION_KEY);
  return false;
}

function requireLogin(){
  const u = localStorage.getItem(SESSION_KEY);
  if(!u){
    alert("Please login first!");
    window.location.href = "login.html";
    return false;
  }
  return true;
}

async function requireLoginServer(){
  const hasUser = requireLogin();
  if(!hasUser) return false;
  const active = await checkServerSession();
  if(!active){
    alert('Session expired or not logged in on server. Please login again.');
    window.location.href = 'login.html';
    return false;
  }
  return true;
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
      // Check if there was a pending flight selection
      const selectedFlight = localStorage.getItem("ars_selectedFlight");
      if(selectedFlight){
        window.location.href = "flight_confirm.html";
      } else {
        window.location.href = "index.html";
      }
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

  // requireLogin(); // Allow search without login

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

function loadConfirmation(){
  requireLogin();

  const search = JSON.parse(localStorage.getItem("ars_search") || "{}");
  const selectedFlight = JSON.parse(localStorage.getItem("ars_selectedFlight") || "{}");

  if(!selectedFlight.flightNumber){
    alert("Please select a flight first!");
    window.location.href = "index.html";
    return;
  }

  // Fetch flight details
  fetch('/api/flights')
    .then(response => response.json())
    .then(flights => {
      const flight = flights.find(f => f.flight_number === selectedFlight.flightNumber && f.from === selectedFlight.from && f.to === selectedFlight.to && f.date === selectedFlight.date);
      if(flight){
        document.getElementById("flightDetails").innerHTML = `
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
              <div class="price">₹${selectedFlight.totalPrice} <small>for ${search.seats} passenger${search.seats > 1 ? 's' : ''}</small></div>
            </div>
          </div>
        `;
        calcFareConfirm();
      } else {
        alert("Flight details not found!");
        window.location.href = "index.html";
      }
    })
    .catch(error => {
      alert("Error loading flight details: " + error.message);
    });
}

function calcFareConfirm(){
  const selectedFlight = JSON.parse(localStorage.getItem("ars_selectedFlight") || "{}");
  const search = JSON.parse(localStorage.getItem("ars_search") || "{}");
  const seats = search.seats || 1;

  let basePerSeat = selectedFlight.totalPrice / seats;
  const base = basePerSeat * seats;
  const tax = Math.round(base * 0.12);
  const total = base + tax;

  document.getElementById("baseFare").innerText = "₹" + base;
  document.getElementById("taxFare").innerText = "₹" + tax;
  document.getElementById("totalFare").innerText = "₹" + total;

  localStorage.setItem("ars_fare", JSON.stringify({base,tax,total,seats}));
}

function confirmBooking(){
  // Proceed to reservation
  window.location.href = "reservation.html";
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

  // Proceed to confirmation
  window.location.href = "flight_confirm.html";
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
  document.getElementById("travelClass").value = "Economy"; // Default

  generatePassengerForms(search.seats);

  calcFare();
}

function generatePassengerForms(seats){
  const search = JSON.parse(localStorage.getItem("ars_search") || "{}");
  const isInternational = !['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Hyderabad'].includes(search.to);

  const container = document.getElementById("passengerForms");
  container.innerHTML = "";

  for(let i = 1; i <= seats; i++){
    const visaFields = isInternational ? `
        <div>
          <label class="form-label">Visa Required</label>
          <input class="form-control" id="visaRequired${i}" type="checkbox" onchange="toggleVisaFile(${i})">
        </div>
        <div id="visaFileDiv${i}" style="display:none;">
          <label class="form-label">Visa Upload</label>
          <input class="form-control" id="visaFile${i}" type="file" accept="image/*,application/pdf">
        </div>
    ` : '';

    const form = document.createElement("div");
    form.className = "passenger-form";
    form.innerHTML = `
      <h4>Passenger ${i}</h4>
      <div class="form-grid">
        <div>
          <label class="form-label">Name</label>
          <input class="form-control" id="name${i}" type="text" placeholder="Enter name" required>
        </div>
        <div>
          <label class="form-label">Phone</label>
          <input class="form-control" id="phone${i}" type="tel" placeholder="Enter phone" pattern="[0-9]{10}" required>
        </div>
        <div>
          <label class="form-label">Aadhar Number</label>
          <input class="form-control" id="aadhar${i}" type="text" placeholder="12-digit Aadhar" pattern="[0-9]{12}" maxlength="12" required>
        </div>
        <div>
          <label class="form-label">Aadhar Upload</label>
          <input class="form-control" id="aadharFile${i}" type="file" accept="image/*,application/pdf" required>
        </div>
        <div>
          <label class="form-label">Passport Number ${isInternational ? '(Required)' : '(Optional)'}</label>
          <input class="form-control" id="passport${i}" type="text" placeholder="Enter passport" ${isInternational ? 'required' : ''}>
        </div>
        <div>
          <label class="form-label">Passport Upload ${isInternational ? '(Required)' : '(Optional)'}</label>
          <input class="form-control" id="passportFile${i}" type="file" accept="image/*,application/pdf" ${isInternational ? 'required' : ''}>
        </div>
        ${visaFields}
        <div class="full">
          <label class="form-label">Address</label>
          <textarea class="form-control" id="address${i}" rows="2" placeholder="Enter address" required></textarea>
        </div>
      </div>
    `;
    container.appendChild(form);
  }
}

function toggleVisaFile(i){
  const checked = document.getElementById(`visaRequired${i}`).checked;
  document.getElementById(`visaFileDiv${i}`).style.display = checked ? 'block' : 'none';
  document.getElementById(`visaFile${i}`).required = checked;
}

function calcFare(){
  const selectedFlight = JSON.parse(localStorage.getItem("ars_selectedFlight") || "{}");
  const search = JSON.parse(localStorage.getItem("ars_search") || "{}");
  const cls = document.getElementById("travelClass").value;
  const seats = search.seats;

  let basePerSeat;
  if(selectedFlight.totalPrice){
    // Use selected flight price
    basePerSeat = selectedFlight.totalPrice / seats;
  } else {
    // Fallback
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

async function sendOTP(){
  const search = JSON.parse(localStorage.getItem("ars_search") || "{}");
  const phone = document.getElementById("phone1").value.trim(); // Use first passenger's phone

  if(!phone || !/^\d{10}$/.test(phone)){
    alert("Please enter a valid 10-digit phone number for the first passenger!");
    return;
  }

  try {
    const response = await fetch('/api/send_otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    const data = await response.json();
    if (response.ok) {
      alert(data.message + " (Mock OTP: 123456)");
      document.getElementById("otpSection").style.display = "block";
    } else {
      alert(data.error || "Failed to send OTP");
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

async function verifyOTP(){
  const otp = document.getElementById("otpInput").value.trim();
  const phone = document.getElementById("phone1").value.trim();

  if(!otp || otp.length !== 6){
    alert("Please enter 6-digit OTP!");
    return;
  }

  try {
    const response = await fetch('/api/verify_otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ otp, phone })
    });
    const data = await response.json();
    if (response.ok) {
      alert("OTP verified!");
      document.getElementById("bookSection").style.display = "block";
    } else {
      alert(data.error || "Invalid OTP");
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

async function proceedTicket(){
  const loggedIn = await requireLoginServer();
  if(!loggedIn) return;

  const search = JSON.parse(localStorage.getItem("ars_search") || "{}");
  const fare = JSON.parse(localStorage.getItem("ars_fare") || "{}");
  const isInternational = !['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Hyderabad'].includes(search.to);

  const passengers = [];
  for(let i = 1; i <= search.seats; i++){
    const name = document.getElementById(`name${i}`).value.trim();
    const phone = document.getElementById(`phone${i}`).value.trim();
    const aadhar = document.getElementById(`aadhar${i}`).value.trim();
    const aadharFile = document.getElementById(`aadharFile${i}`).files[0];
    const passport = document.getElementById(`passport${i}`).value.trim();
    const passportFile = document.getElementById(`passportFile${i}`).files[0];
    const address = document.getElementById(`address${i}`).value.trim();
    const visaRequired = document.getElementById(`visaRequired${i}`) ? document.getElementById(`visaRequired${i}`).checked : false;
    const visaFile = visaRequired ? document.getElementById(`visaFile${i}`).files[0] : null;

    if(!name || !phone || !aadhar || !address || !aadharFile){
      alert(`Please fill all details and upload Aadhar for Passenger ${i}!`);
      return;
    }

    if(isInternational && (!passport || !passportFile)){
      alert(`Passport and upload required for international flights for Passenger ${i}!`);
      return;
    }

    let aadharFilename = '';
    if(aadharFile){
      const formData = new FormData();
      formData.append('file', aadharFile);
      const uploadRes = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      const uploadData = await uploadRes.json();
      if(uploadRes.ok){
        aadharFilename = uploadData.filename;
      } else {
        alert(`Failed to upload Aadhar for Passenger ${i}: ${uploadData.error}`);
        return;
      }
    }

    let passportFilename = '';
    if(passportFile){
      const formData = new FormData();
      formData.append('file', passportFile);
      const uploadRes = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      const uploadData = await uploadRes.json();
      if(uploadRes.ok){
        passportFilename = uploadData.filename;
      } else {
        alert(`Failed to upload Passport for Passenger ${i}: ${uploadData.error}`);
        return;
      }
    }

    let visaFilename = '';
    if(visaFile){
      const formData = new FormData();
      formData.append('file', visaFile);
      const uploadRes = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      const uploadData = await uploadRes.json();
      if(uploadRes.ok){
        visaFilename = uploadData.filename;
      } else {
        alert(`Failed to upload Visa for Passenger ${i}: ${uploadData.error}`);
        return;
      }
    }

    passengers.push({ name, phone, aadhar, aadhar_file: aadharFilename, passport, passport_file: passportFilename, address, visa_required: visaRequired, visa_file: visaFilename });
  }

  const bookingData = {
    passengers,
    from: search.from,
    to: search.to,
    date: search.date,
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
        passengers,
        from: search.from,
        to: search.to,
        date: search.date,
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
async function loadConfirm(){
  const loggedIn = await requireLoginServer();
  if(!loggedIn) return;

  const booking = JSON.parse(localStorage.getItem("ars_currentBooking") || "{}");
  if(!booking.ticketId){
    alert("No ticket found!");
    window.location.href = "index.html";
    return;
  }

  document.getElementById("tId").innerText = booking.ticketId;
  document.getElementById("tUser").innerText = booking.user;

  let passengersHtml = "";
  if(booking.passengers && booking.passengers.length > 0){
    passengersHtml = booking.passengers.map(p => `<div><b>${p.name}</b> (Phone: ${p.phone}, Aadhar: ${p.aadhar})</div>`).join('');
  } else {
    passengersHtml = `<div><b>${booking.passengerName}</b> (Phone: ${booking.phone}, Aadhar: ${booking.aadharNumber})</div>`;
  }

  document.getElementById("tPassengers").innerHTML = passengersHtml;
  document.getElementById("tRoute").innerText = booking.from + " → " + booking.to;
  document.getElementById("tDate").innerText = booking.date;
  document.getElementById("tClass").innerText = booking.class;
  document.getElementById("tFare").innerText = "₹" + booking.total;
  document.getElementById("tBooked").innerText = booking.bookedAt;
}

function printTicketPDF(){
  // Browser will open Print dialog -> choose "Save as PDF"
  window.print();
}

// ---------- MY BOOKINGS ----------
async function loadMyBookings(){
  const loggedIn = await requireLoginServer();
  if(!loggedIn) return;

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

      let passengersHtml = b.passengers.map(p => `<div><b>${p.name}</b> (${p.phone}, Aadhar: ${p.aadhar_number})</div>`).join('');

      div.innerHTML = `
        <div class="ticket-grid">
          <div><b>Ticket ID:</b> ${b.ticket_id}</div>
          <div><b>Booked At:</b> ${b.booked_at}</div>
          <div class="full"><b>Passengers:</b></div>
          <div class="full">${passengersHtml}</div>
          <div><b>Route:</b> ${b.from_city} → ${b.to_city}</div>
          <div><b>Date:</b> ${b.travel_date}</div>
          <div><b>Class:</b> ${b.travel_class}</div>
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
      passengers: found.passengers,
      from: found.from_city,
      to: found.to_city,
      date: found.travel_date,
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
  const confirmation = prompt("Type CANCEL to confirm cancellation:");
  if(confirmation !== "CANCEL"){
    alert("Cancellation aborted.");
    return;
  }

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