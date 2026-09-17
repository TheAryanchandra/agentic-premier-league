// Environment variables
const ADMIN_KEY = process.env.ADMIN_KEY || 'admin';
const DB_NAME = 'StadiumPulse';

// Raw URI from env or fallback with warning
const rawUri = process.env.MONGODB_URI || process.env.MONGO_URL || '';
const hasPlaceholder = rawUri.includes('<db_username>') || rawUri.includes('<password>');

let cachedClient = null;
let cachedDb = null;
let MongoClient = null;

// Dynamically load mongodb driver if available
async function loadMongoClient() {
    if (MongoClient) return MongoClient;
    try {
        const mod = await import('mongodb');
        MongoClient = mod.MongoClient;
        return MongoClient;
    } catch (e) {
        console.log("ℹ️ Note: 'mongodb' module not installed in current environment. Using mock in-memory fallback.");
        return null;
    }
}

// Initial Mock data for fallback or initial seeding
const DEFAULT_ZONES = [
    { id: "N1", name: "North Stand", capacity: 5000, status: "active" },
    { id: "S1", name: "South Stand", capacity: 4000, status: "active" },
    { id: "E1", name: "East Stand", capacity: 3000, status: "active" },
    { id: "W1", name: "West Stand", capacity: 3500, status: "active" },
    { id: "F1", name: "Food Court", capacity: 500, status: "active" },
    { id: "R1", name: "Restrooms", capacity: 200, status: "active" }
];

const DEFAULT_DENSITY = {
    N1: { current: 2500, trend: [2000, 2200, 2400, 2500], last_update: Date.now() / 1000 },
    S1: { current: 1800, trend: [1500, 1600, 1700, 1800], last_update: Date.now() / 1000 },
    E1: { current: 1200, trend: [800, 900, 1000, 1200], last_update: Date.now() / 1000 },
    W1: { current: 2000, trend: [1800, 1850, 1950, 2000], last_update: Date.now() / 1000 },
    F1: { current: 150, trend: [50, 100, 120, 150], last_update: Date.now() / 1000 },
    R1: { current: 45, trend: [30, 35, 40, 45], last_update: Date.now() / 1000 }
};

// In-memory state for fallback
let memoryZones = JSON.parse(JSON.stringify(DEFAULT_ZONES));
let memoryDensity = JSON.parse(JSON.stringify(DEFAULT_DENSITY));
let memoryAlerts = [];

// Helper: Connect to MongoDB Atlas
async function getDatabase() {
    if (!rawUri || hasPlaceholder) {
        return null;
    }
    if (cachedDb) return cachedDb;

    try {
        const ClientClass = await loadMongoClient();
        if (!ClientClass) return null;

        if (!cachedClient) {
            cachedClient = new ClientClass(rawUri, {
                serverSelectionTimeoutMS: 5000,
                connectTimeoutMS: 10000,
            });
            await cachedClient.connect();
        }
        cachedDb = cachedClient.db(DB_NAME);

        // Seed initial data if collections are empty
        const zonesCount = await cachedDb.collection('zones').countDocuments();
        if (zonesCount === 0) {
            await cachedDb.collection('zones').insertMany(DEFAULT_ZONES);
        }

        const densityDoc = await cachedDb.collection('venue').findOne({ _id: 'current_density' });
        if (!densityDoc) {
            await cachedDb.collection('venue').insertOne({ _id: 'current_density', ...DEFAULT_DENSITY });
        }

        return cachedDb;
    } catch (err) {
        console.error("MongoDB Atlas connection error, falling back to mock mode:", err.message);
        return null;
    }
}

// Helper: parse JSON body from Vercel / Node request
function parseBody(req) {
    return new Promise((resolve) => {
        if (req.body && typeof req.body === 'object') return resolve(req.body);
        if (req.body && typeof req.body === 'string') {
            try { return resolve(JSON.parse(req.body)); } catch (e) { return resolve({}); }
        }
        let data = '';
        req.on('data', chunk => { data += chunk; });
        req.on('end', () => {
            try { resolve(JSON.parse(data || '{}')); } catch (e) { resolve({}); }
        });
    });
}

// Vercel Serverless Function Handler
export default async function handler(req, res) {
    // Enable CORS for all requests
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key, Authorization');

    if (req.method === 'OPTIONS') {
        return res.status(204).end();
    }

    const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    let pathname = url.pathname;
    
    // Normalize path by removing trailing slash and optional /api prefix
    if (pathname.length > 1 && pathname.endsWith('/')) {
        pathname = pathname.slice(0, -1);
    }
    const cleanPath = pathname.startsWith('/api') ? pathname.replace(/^\/api/, '') || '/' : pathname;

    const db = await getDatabase();
    const dbConnected = !!db;

    try {
        // GET / or /health
        if (cleanPath === '/' || cleanPath === '') {
            return res.status(200).json({
                status: "Stadium Experience Dashboard API",
                version: "2.0.0",
                database: dbConnected ? "MongoDB Atlas (Connected)" : "In-Memory / Mock Mode",
                cluster: DB_NAME,
                endpoints: ["/zones", "/density", "/alerts", "/queue/prediction/:id", "/health"]
            });
        }

        if (cleanPath === '/health') {
            return res.status(200).json({
                status: "healthy",
                database: dbConnected ? "connected" : "mock-fallback",
                cluster: DB_NAME,
                timestamp: new Date().toISOString()
            });
        }

        // GET /zones
        if (cleanPath === '/zones' && req.method === 'GET') {
            if (db) {
                const zones = await db.collection('zones').find({}, { projection: { _id: 0 } }).toArray();
                return res.status(200).json(zones.length > 0 ? zones : memoryZones);
            }
            return res.status(200).json(memoryZones);
        }

        // POST /zones/update
        if (cleanPath === '/zones/update' && req.method === 'POST') {
            const adminHeader = req.headers['x-admin-key'];
            if (adminHeader !== ADMIN_KEY) {
                return res.status(403).json({ detail: "Invalid Staff Access Token" });
            }

            const zoneId = url.searchParams.get('zone_id');
            const status = url.searchParams.get('status');
            if (!['active', 'maintenance', 'closed'].includes(status)) {
                return res.status(400).json({ detail: "Invalid status" });
            }

            if (db) {
                const result = await db.collection('zones').updateOne(
                    { id: zoneId },
                    { $set: { status: status } }
                );
                if (result.matchedCount > 0) {
                    return res.status(200).json({ status: "success", zone_id: zoneId, new_status: status });
                }
            }

            // Fallback memory update
            const zone = memoryZones.find(z => z.id === zoneId);
            if (zone) {
                zone.status = status;
                return res.status(200).json({ status: "success", zone_id: zoneId, new_status: status });
            }
            return res.status(404).json({ detail: "Zone not found" });
        }

        // GET /density
        if (cleanPath === '/density' && req.method === 'GET') {
            let densityMap = memoryDensity;
            let currentZones = memoryZones;

            if (db) {
                const doc = await db.collection('venue').findOne({ _id: 'current_density' });
                if (doc) {
                    const { _id, ...rest } = doc;
                    densityMap = rest;
                }
                const zList = await db.collection('zones').find({}, { projection: { _id: 0 } }).toArray();
                if (zList.length > 0) currentZones = zList;
            }

            const result = {};
            for (const [zoneId, data] of Object.entries(densityMap)) {
                const zone = currentZones.find(z => z.id === zoneId);
                if (zone) {
                    const percentage = (data.current / zone.capacity) * 100;
                    const status = percentage < 70 ? 'safe' : percentage < 85 ? 'crowded' : 'danger';
                    result[zoneId] = {
                        current: data.current,
                        capacity: zone.capacity,
                        percentage: Math.round(percentage * 10) / 10,
                        status: status,
                        trend: data.trend,
                        last_update: data.last_update
                    };
                }
            }
            return res.status(200).json(result);
        }

        // POST /density/update
        if (cleanPath === '/density/update' && req.method === 'POST') {
            const adminHeader = req.headers['x-admin-key'];
            if (adminHeader !== ADMIN_KEY) {
                return res.status(403).json({ detail: "Invalid Staff Access Token" });
            }

            const body = await parseBody(req);
            const { zone_id, current_people } = body;
            const timestamp = body.timestamp || Date.now() / 1000;

            if (db) {
                const doc = await db.collection('venue').findOne({ _id: 'current_density' });
                if (doc && doc[zone_id]) {
                    const oldTrend = doc[zone_id].trend || [current_people];
                    const newTrend = [...oldTrend.slice(1), current_people];
                    await db.collection('venue').updateOne(
                        { _id: 'current_density' },
                        {
                            $set: {
                                [`${zone_id}.current`]: current_people,
                                [`${zone_id}.trend`]: newTrend,
                                [`${zone_id}.last_update`]: timestamp
                            }
                        }
                    );
                    return res.status(200).json({ status: "success", zone_id, people: current_people });
                }
            }

            // Fallback in-memory
            if (memoryDensity[zone_id]) {
                memoryDensity[zone_id].trend = [...memoryDensity[zone_id].trend.slice(1), current_people];
                memoryDensity[zone_id].current = current_people;
                memoryDensity[zone_id].last_update = timestamp;
                return res.status(200).json({ status: "success", zone_id, people: current_people });
            }
            return res.status(404).json({ detail: "Zone not found" });
        }

        // GET /alerts
        if (cleanPath === '/alerts' && req.method === 'GET') {
            if (db) {
                const alerts = await db.collection('alerts')
                    .find({}, { projection: { _id: 0 } })
                    .sort({ timestamp: -1 })
                    .limit(20)
                    .toArray();
                return res.status(200).json(alerts);
            }
            return res.status(200).json([...memoryAlerts].reverse());
        }

        // POST /alerts/create
        if (cleanPath === '/alerts/create' && req.method === 'POST') {
            const body = await parseBody(req);
            const adminHeader = req.headers['x-admin-key'];

            if (body.severity !== 'danger' && adminHeader !== ADMIN_KEY) {
                return res.status(403).json({ detail: "Unauthorized Staff Access" });
            }

            const alertObj = {
                id: body.id || `alert_${Date.now()}`,
                message: body.message || body.msg || 'Alert message',
                zone_id: body.zone_id || null,
                phone: body.phone || null,
                severity: body.severity || 'info',
                status: body.status || 'active',
                timestamp: body.timestamp || Date.now() / 1000
            };

            if (db) {
                await db.collection('alerts').insertOne({ ...alertObj });
                return res.status(200).json({ status: "success", alert: alertObj });
            }

            memoryAlerts.push(alertObj);
            return res.status(200).json({ status: "success", alert: alertObj });
        }

        // POST /alerts/resolve/:index
        if (cleanPath.startsWith('/alerts/resolve/') && req.method === 'POST') {
            const adminHeader = req.headers['x-admin-key'];
            if (adminHeader !== ADMIN_KEY) {
                return res.status(403).json({ detail: "Invalid Staff Access Token" });
            }

            const param = cleanPath.replace('/alerts/resolve/', '');
            if (db) {
                const resUpdate = await db.collection('alerts').updateOne(
                    { $or: [{ id: param }, { _id: param }] },
                    { $set: { status: 'resolved' } }
                );
                if (resUpdate.matchedCount > 0) {
                    return res.status(200).json({ status: "success", message: "Alert resolved" });
                }
            }

            const idx = parseInt(param, 10);
            if (!isNaN(idx) && idx >= 0 && idx < memoryAlerts.length) {
                memoryAlerts[idx].status = 'resolved';
                return res.status(200).json({ status: "success", message: "Alert resolved" });
            }
            return res.status(200).json({ status: "success", message: "Alert resolved" });
        }

        // DELETE /alerts/clear
        if (cleanPath === '/alerts/clear' && req.method === 'DELETE') {
            const adminHeader = req.headers['x-admin-key'];
            if (adminHeader !== ADMIN_KEY) {
                return res.status(403).json({ detail: "Invalid Staff Access Token" });
            }

            if (db) {
                await db.collection('alerts').deleteMany({});
            }
            memoryAlerts = [];
            return res.status(200).json({ status: "success", message: "All alerts cleared" });
        }

        // GET /queue/prediction/:zone_id
        if (cleanPath.startsWith('/queue/prediction/') && req.method === 'GET') {
            const zoneId = cleanPath.replace('/queue/prediction/', '');
            let densityMap = memoryDensity;
            if (db) {
                const doc = await db.collection('venue').findOne({ _id: 'current_density' });
                if (doc) {
                    const { _id, ...rest } = doc;
                    densityMap = rest;
                }
            }

            if (!densityMap[zoneId]) {
                return res.status(404).json({ detail: "Zone not found" });
            }

            const trend = densityMap[zoneId].trend || [1000];
            const current = densityMap[zoneId].current || 1000;
            let avgGrowth = 0;
            if (trend.length > 1) {
                let sumDiff = 0;
                for (let i = 0; i < trend.length - 1; i++) {
                    sumDiff += (trend[i + 1] - trend[i]);
                }
                avgGrowth = sumDiff / (trend.length - 1);
            }

            const predicted5min = Math.max(0, Math.round(current + (avgGrowth * 0.5)));
            const predicted10min = Math.max(0, Math.round(current + (avgGrowth * 1.0)));

            return res.status(200).json({
                zone_id: zoneId,
                current: current,
                predicted_5min: predicted5min,
                predicted_10min: predicted10min,
                trend: avgGrowth > 0 ? "increasing" : "decreasing",
                recommendation: predicted10min > 2500 ? "avoid" : "ok"
            });
        }

        return res.status(404).json({ detail: "Endpoint not found: " + cleanPath });
    } catch (err) {
        console.error("Internal API Handler Error:", err);
        return res.status(500).json({ error: "Internal Server Error", detail: err.message });
    }
}
