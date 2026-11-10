
const API="/api/incidents";

let incidents=[];
let teams=[];
let emergencyMap=null;
let incidentLayer=null;
let teamLayer=null;
let routeLayer=null;

function esc(value){
    return String(value??"").replace(/[&<>"']/g,c=>({
        "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
    })[c]);
}

function color(level){
    return {
        Critical:"#e5223e",
        High:"#f07821",
        Medium:"#eab308",
        Low:"#16a34a"
    }[level]||"#347bd1";
}

async function fetchJSON(url,options={}){
    const response=await fetch(url,options);
    const result=await response.json();
    if(!response.ok)throw new Error(result.error||"Request failed.");
    return result;
}


// ==========================================
// AUTOMATIC TEAM LOCATION DETECTION
// ==========================================

let lastGeocodedLocation="";

document.getElementById("teamLocation").addEventListener("input",()=>{
    lastGeocodedLocation="";
    document.getElementById("teamLatitude").value="";
    document.getElementById("teamLongitude").value="";
    document.getElementById("locationMessage").textContent=
        "Location changed. Find coordinates again.";
    document.getElementById("locationMessage").style.color="#718198";
});

async function findTeamCoordinates(){

    const location=document.getElementById("teamLocation").value.trim();
    const latitudeInput=document.getElementById("teamLatitude");
    const longitudeInput=document.getElementById("teamLongitude");
    const message=document.getElementById("locationMessage");
    const button=document.getElementById("findCoordinates");

    if(!location){
        message.textContent="Please enter a team location first.";
        message.style.color="#dc3545";
        return;
    }

    button.disabled=true;
    button.innerHTML='<i class="fa-solid fa-spinner fa-spin"></i> Finding...';
    message.textContent="Searching for geographical coordinates...";
    message.style.color="#718198";

    try{

        const query=encodeURIComponent(location+", Tamil Nadu, India");

        const response=await fetch(
            `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=${query}`,
            {headers:{"Accept":"application/json"}}
        );

        if(!response.ok){
            throw new Error("Location service unavailable. Try again.");
        }

        const results=await response.json();

        if(!results.length){
            throw new Error("Location not found. Enter a more specific location.");
        }

        const place=results[0];
        const lat=Number(place.lat);
        const lon=Number(place.lon);

        if(!Number.isFinite(lat)||!Number.isFinite(lon)){
            throw new Error("Invalid coordinates received.");
        }

        latitudeInput.value=lat.toFixed(6);
        longitudeInput.value=lon.toFixed(6);
        lastGeocodedLocation=location;

        message.innerHTML=
            '<i class="fa-solid fa-circle-check"></i> Location found: '+
            esc(place.display_name);

        message.style.color="#16804a";

    }catch(error){

        latitudeInput.value="";
        longitudeInput.value="";
        lastGeocodedLocation="";

        message.textContent=error.message;
        message.style.color="#dc3545";

    }finally{

        button.disabled=false;
        button.innerHTML=
            '<i class="fa-solid fa-location-crosshairs"></i> Find Location';

    }
}


// ==========================================
// MAP
// ==========================================

function initializeMap(){

    if(emergencyMap||!window.L)return;

    emergencyMap=L.map("incidentMap").setView([11.5,78.5],7);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{
        attribution:"&copy; OpenStreetMap contributors",
        maxZoom:19
    }).addTo(emergencyMap);

    incidentLayer=L.layerGroup().addTo(emergencyMap);
    teamLayer=L.layerGroup().addTo(emergencyMap);
    routeLayer=L.layerGroup().addTo(emergencyMap);

    setTimeout(()=>emergencyMap.invalidateSize(),300);
}

function validGPS(item){
    return item.latitude!==null&&item.longitude!==null&&
        Number.isFinite(Number(item.latitude))&&
        Number.isFinite(Number(item.longitude))&&
        Math.abs(Number(item.latitude))<=90&&
        Math.abs(Number(item.longitude))<=180;
}

function updateMap(){

    initializeMap();

    if(!emergencyMap)return;

    incidentLayer.clearLayers();
    teamLayer.clearLayers();
    routeLayer.clearLayers();

    const points=[];
    const teamById={};

    incidents.filter(validGPS).forEach(item=>{

        const lat=Number(item.latitude);
        const lon=Number(item.longitude);

        const marker=L.circleMarker([lat,lon],{
            radius:9,
            color:color(item.severity),
            fillColor:color(item.severity),
            fillOpacity:.9,
            weight:2
        });

        marker.bindPopup(`
            <b>#${item.id} ${esc(item.title)}</b>
            <p>${esc(item.category)}</p>
            <p>Priority: ${esc(item.severity)} (${item.score}/100)</p>
            <p>Status: ${esc(item.status)}</p>
            <p>Team: ${esc(item.team)}</p>
        `);

        marker.addTo(incidentLayer);
        points.push([lat,lon]);
    });

    teams.forEach(team=>{

        teamById[team.id]=team;

        const lat=Number(team.latitude);
        const lon=Number(team.longitude);

        if(!Number.isFinite(lat)||!Number.isFinite(lon))return;

        L.marker([lat,lon])
        .bindPopup(`
            <b>${esc(team.name)}</b>
            <p>${esc(team.team_code)}</p>
            <p>${esc(team.category)}</p>
            <p>${esc(team.availability)}</p>
        `)
        .addTo(teamLayer);

        points.push([lat,lon]);
    });

    incidents.forEach(item=>{

        if(!validGPS(item)||!item.team_id)return;

        const team=teamById[item.team_id];

        if(!team)return;

        L.polyline([
            [Number(team.latitude),Number(team.longitude)],
            [Number(item.latitude),Number(item.longitude)]
        ],{
            color:"#347bd1",
            weight:3,
            opacity:.75,
            dashArray:"8,8"
        }).addTo(routeLayer);
    });

    if(points.length){
        emergencyMap.fitBounds(points,{padding:[35,35],maxZoom:14});
    }
}


// ==========================================
// LOAD ALL DATA
// ==========================================

async function loadAll(){

    try{

        const results=await Promise.all([
            fetchJSON(API),
            fetchJSON("/api/teams"),
            fetchJSON("/api/analytics")
        ]);

        incidents=results[0];
        teams=results[1];

        updateDashboard(results[2]);
        updateIncidentTable();
        updateTeamTable();
        updateAnalytics(results[2]);
        updateDuplicates();
        updateMap();

    }catch(error){

        console.error(error);

        document.getElementById("incidentTable").innerHTML=
            `<tr><td colspan="8">${esc(error.message)}</td></tr>`;
    }
}


// ==========================================
// DASHBOARD COUNTS
// ==========================================

function updateDashboard(a){

    document.getElementById("total").textContent=a.total;
    document.getElementById("critical").textContent=a.critical;
    document.getElementById("pending").textContent=a.pending;
    document.getElementById("resolved").textContent=a.resolved;

    document.getElementById("teamsTotal").textContent=a.teams_total;
    document.getElementById("teamsAvailable").textContent=a.teams_available;
    document.getElementById("teamsBusy").textContent=a.teams_busy;
    document.getElementById("teamsUnavailable").textContent=a.teams_unavailable;
}


// ==========================================
// ANALYTICS
// ==========================================

function updateAnalytics(a){

    const categoryBox=document.getElementById("categoryList");
    const severityBox=document.getElementById("severityList");

    const categories=[
        "Fire Emergency","Road Accident","Medical Emergency",
        "Flood","Building Collapse","Other Emergencies"
    ];

    categoryBox.innerHTML=categories.map(category=>{

        const item=a.categories.find(x=>x.category===category);
        const count=item?item.count:0;
        const pct=a.total?count/a.total*100:0;

        return `
        <div class="category-row">
            <div class="category-name">
                ${esc(category)}
                <div class="category-bar">
                    <span style="width:${pct}%"></span>
                </div>
            </div>
            <strong>${count}</strong>
        </div>`;
    }).join("");

    const levels=["Critical","High","Medium","Low"];

    severityBox.innerHTML=levels.map(level=>{

        const item=a.severity.find(x=>x.severity===level);

        return `
        <div class="severity-row">
            <span class="pill sev-${level}">${level}</span>
            <strong>${item?item.count:0}</strong>
        </div>`;
    }).join("");
}


// ==========================================
// INCIDENT FILTERS
// ==========================================

function updateIncidentTable(){

    const search=document.getElementById("searchInput").value.toLowerCase();
    const severity=document.getElementById("severityFilter").value;
    const category=document.getElementById("categoryFilter").value;
    const status=document.getElementById("statusFilter").value;

    const filtered=incidents.filter(r=>{

        const text=[r.id,r.title,r.location,r.category,r.reporter]
            .some(v=>String(v??"").toLowerCase().includes(search));

        return text&&(!severity||r.severity===severity)&&
            (!category||r.category===category)&&
            (!status||r.status===status);
    });

    const table=document.getElementById("incidentTable");

    document.getElementById("recordCount").textContent=
        `${filtered.length} incident(s) displayed`;

    if(!filtered.length){
        table.innerHTML="<tr><td colspan='8'>No incidents found.</td></tr>";
        return;
    }

    table.innerHTML=filtered.map(r=>`
    <tr>
        <td><b>#${r.id}</b></td>
        <td>
            <b>${esc(r.title)}</b>
            <small class="table-sub">${Number(r.affected)||0} people affected</small>
        </td>
        <td>${esc(r.category)}</td>
        <td>${esc(r.location)}</td>
        <td>
            <span class="pill sev-${esc(r.severity)}">${esc(r.severity)}</span>
            <small class="table-sub">Score: ${r.score}/100</small>
        </td>
        <td>
            <b>${esc(r.team)}</b>
            <small class="table-sub">${r.team_id?"Assigned":"Unassigned"}</small>
        </td>
        <td>
            <span class="pill st-${String(r.status).replaceAll(" ","-")}">${esc(r.status)}</span>
        </td>
        <td>
            <div class="row-actions">
                <button class="view-btn" onclick="showDetails(${r.id})">
                    <i class="fa-solid fa-eye"></i>
                </button>
                <button class="view-btn" onclick="assignNearest(${r.id})">
                    <i class="fa-solid fa-location-arrow"></i>
                </button>
                <select class="status-select" onchange="updateStatus(${r.id},this.value)">
                    <option value="">Status</option>
                    ${["Reported","Assigned","In Progress","Resolved"].map(s=>
                        `<option value="${s}">${s}</option>`
                    ).join("")}
                </select>
                <button class="delete-btn" onclick="deleteIncident(${r.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        </td>
    </tr>`).join("");
}


// ==========================================
// REGISTER TEAM
// ==========================================

document.getElementById("teamForm").addEventListener("submit",async e=>{

    e.preventDefault();

    const message=document.getElementById("teamMessage");
    const location=document.getElementById("teamLocation").value.trim();

    if(lastGeocodedLocation!==location){
        message.style.color="#c72f46";
        message.textContent="Please find the coordinates again for the current location.";
        return;
    }

    const data={
        name:document.getElementById("teamName").value,
        team_code:document.getElementById("teamCode").value,
        category:document.getElementById("teamCategory").value,
        location:location,
        latitude:document.getElementById("teamLatitude").value,
        longitude:document.getElementById("teamLongitude").value,
        phone:document.getElementById("teamPhone").value
    };

    try{

        await fetchJSON("/api/teams",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify(data)
        });

        message.style.color="#16804a";
        message.textContent="Response team added successfully.";

        e.target.reset();
        lastGeocodedLocation="";

        document.getElementById("locationMessage").textContent=
            "Enter a location and click Find Location.";

        await loadAll();

    }catch(error){

        message.style.color="#c72f46";
        message.textContent=error.message;
    }
});


// ==========================================
// TEAM TABLE
// ==========================================

function updateTeamTable(){

    const box=document.getElementById("teamTable");

    if(!teams.length){
        box.innerHTML="<tr><td colspan='6'>No response teams registered.</td></tr>";
        return;
    }

    box.innerHTML=teams.map(t=>`
    <tr>
        <td><b>${esc(t.team_code)}</b></td>
        <td>${esc(t.name)}<small class="table-sub">${esc(t.phone)}</small></td>
        <td>${esc(t.category)}</td>
        <td>${esc(t.location)}
            <small class="table-sub">${Number(t.latitude).toFixed(5)}, ${Number(t.longitude).toFixed(5)}</small>
        </td>
        <td>
            <select class="status-select" onchange="updateTeamAvailability(${t.id},this.value)">
                ${["Available","Busy","Unavailable"].map(s=>
                    `<option value="${s}" ${t.availability===s?"selected":""}>${s}</option>`
                ).join("")}
            </select>
        </td>
        <td>
            <button class="delete-btn" onclick="deleteTeam(${t.id})">
                <i class="fa-solid fa-trash"></i>
            </button>
        </td>
    </tr>`).join("");
}

async function updateTeamAvailability(id,availability){

    try{

        await fetchJSON(`/api/teams/${id}`,{
            method:"PATCH",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({availability})
        });

        await loadAll();

    }catch(error){

        alert(error.message);
        await loadAll();
    }
}

async function deleteTeam(id){

    if(!confirm("Delete this response team?"))return;

    try{
        await fetchJSON(`/api/teams/${id}`,{method:"DELETE"});
        await loadAll();
    }catch(error){
        alert(error.message);
    }
}


// ==========================================
// AUTOMATIC NEAREST TEAM ASSIGNMENT
// ==========================================

async function assignNearest(id){

    try{

        const result=await fetchJSON(`${API}/${id}/assign`,{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({})
        });

        alert(`Assigned ${result.name} (${result.distance} km away).`);

        await loadAll();

    }catch(error){
        alert(error.message);
    }
}


// ==========================================
// STATUS UPDATE
// ==========================================

async function updateStatus(id,status){

    if(!status)return;

    try{

        await fetchJSON(`${API}/${id}`,{
            method:"PATCH",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({status})
        });

        await loadAll();

    }catch(error){

        alert(error.message);
        await loadAll();
    }
}


// ==========================================
// DELETE INCIDENT
// ==========================================

async function deleteIncident(id){

    if(!confirm(`Delete incident #${id}?`))return;

    try{
        await fetchJSON(`${API}/${id}`,{method:"DELETE"});
        await loadAll();
    }catch(error){
        alert(error.message);
    }
}


// ==========================================
// INCIDENT DETAILS
// ==========================================

function showDetails(id){

    const r=incidents.find(x=>x.id===id);

    if(!r)return;

    const fields=[
        ["Incident ID","#"+r.id],
        ["Title",r.title],
        ["Description",r.description],
        ["Category",r.category],
        ["Location",r.location],
        ["Affected people",r.affected],
        ["Reporter",r.reporter],
        ["Contact",r.contact||"Not provided"],
        ["Priority score",r.score+"/100"],
        ["Severity",r.severity],
        ["Analysis",r.ai_reason],
        ["Recommended action",r.recommended_action],
        ["Assigned team",r.team],
        ["Status",r.status],
        ["Submitted",r.created],
        ["Potential duplicate",r.duplicate_of?"#"+r.duplicate_of:"None"]
    ];

    let html=fields.map(([a,b])=>`
        <div class="detail-line">
            <strong>${esc(a)}</strong>${esc(b)}
        </div>
    `).join("");

    if(r.photo){
        html+=`
        <div class="detail-line">
            <strong>Photo evidence</strong>
            <img class="detail-photo" src="/static/uploads/${encodeURIComponent(r.photo)}">
        </div>`;
    }

    if(validGPS(r)){
        html+=`
        <a class="btn btn-blue detail-map" target="_blank" rel="noopener"
        href="https://www.google.com/maps?q=${encodeURIComponent(r.latitude)},${encodeURIComponent(r.longitude)}">
        Open incident location
        </a>`;
    }

    document.getElementById("detailContent").innerHTML=html;
    document.getElementById("detailModal").classList.add("show");
}

function closeDetails(){
    document.getElementById("detailModal").classList.remove("show");
}


// ==========================================
// DUPLICATE REPORTS
// ==========================================

function updateDuplicates(){

    const matches=incidents.filter(r=>r.duplicate_of);
    const box=document.getElementById("duplicateList");

    if(!matches.length){
        box.innerHTML="<p class='empty-message'>No potential duplicate reports found.</p>";
        return;
    }

    box.innerHTML=matches.map(r=>`
        <div class="duplicate-item">
            <b>Report #${r.id}</b> may be similar to report #${r.duplicate_of}.
            <p>${esc(r.title)} · ${esc(r.location)}</p>
        </div>
    `).join("");
}


// ==========================================
// EVENT LISTENERS
// ==========================================

["searchInput","severityFilter","categoryFilter","statusFilter"].forEach(id=>{

    document.getElementById(id).addEventListener(
        id==="searchInput"?"input":"change",
        updateIncidentTable
    );

});

document.getElementById("detailModal").addEventListener("click",e=>{
    if(e.target.id==="detailModal")closeDetails();
});

loadAll();
setInterval(loadAll,15000);
