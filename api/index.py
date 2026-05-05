from flask import Flask, jsonify, send_file, request, session, redirect
import os, sys, json, numpy as np

app = Flask(__name__)
app.secret_key = 'datacenter-energy-scheduler-2026'

# ========== 原始路由（不动） ==========
@app.route('/api/test')
def test():
    return "✅ API 正常运行"

# ========== 新增路由（前端服务） ==========
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

STUDENTS = {"admin":"admin123","student":"student123","2024001":"123456","demo":"demo"}
USERS_FILE = os.path.join(BASE, 'users.json')
if os.path.exists(USERS_FILE):
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            STUDENTS.update(json.load(f))
    except: pass

def need_login():
    return 'username' not in session

@app.route('/')
def landing():
    if 'username' in session:
        return redirect('/selector')
    return send_file(os.path.join(BASE, 'index.html'))

@app.route('/login-page')
def login_form():
    if 'username' in session:
        return redirect('/selector')
    return send_file(os.path.join(BASE, 'login.html'))

@app.route('/login', methods=['POST'])
def do_login():
    u = request.form.get('username','').strip()
    p = request.form.get('password','').strip()
    nxt = request.form.get('next','/selector')
    if u in STUDENTS and STUDENTS[u] == p:
        session['username'] = u
        return redirect(nxt)
    return redirect('/login-page?error=1')

@app.route('/register-page')
def register_form():
    return send_file(os.path.join(BASE, 'register.html'))

@app.route('/register', methods=['POST'])
def do_register():
    u = request.form.get('username','').strip()
    p = request.form.get('password','').strip()
    if not u or not p:
        return redirect('/register-page?error=empty')
    if u in STUDENTS:
        return redirect('/register-page?error=exists')
    STUDENTS[u] = p
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(STUDENTS, f, ensure_ascii=False)
    except: pass
    session['username'] = u
    return redirect('/selector')

@app.route('/logout')
def do_logout():
    session.clear()
    return redirect('/')

@app.route('/selector')
def selector_page():
    if need_login(): return redirect('/')
    return send_file(os.path.join(BASE, 'selector.html'))

@app.route('/forum')
def forum_page():
    if need_login(): return redirect('/')
    return send_file(os.path.join(BASE, 'forum.html'))

@app.route('/dashboard')
def dashboard_page():
    if need_login(): return redirect('/')
    return send_file(os.path.join(BASE, 'dashboard.html'))

@app.route('/dispatch')
def dispatch_page():
    if need_login(): return redirect('/')
    return send_file(os.path.join(BASE, 'dispatch.html'))

# ========== API 数据端点（对接后端模块） ==========
def gen_pv(h=24):
    t = np.linspace(0, h, h*12)
    s = np.clip(np.sin(np.pi*(t-6)/12), 0, 1)
    c = 0.85 + 0.15*np.sin(np.pi*t/8)
    return (s*c*1280).tolist()

def gen_wind(h=24):
    t = np.linspace(0, h, h*12)
    return (450+100*np.sin(np.pi*t/12+2)+80*np.sin(2*np.pi*t/3.5)).tolist()

def gen_grid(h=24):
    t = np.linspace(0, h, h*12)
    return (320*np.sin(np.pi*(t-8)/10+0.5)+100*np.sin(2*np.pi*t/5)).tolist()

@app.route('/api/dashboard')
def api_dashboard():
    return jsonify({
        "kpi":{"pv":1280,"wind":856,"storage":4200,"charging_pile":32,"cooling":1560,"gas_turbine":920,"transformer":98.5,"peak_demand":3680},
        "pv_power":gen_pv(),"wind_power":gen_wind(),"grid_exchange":gen_grid(),
        "emission":{"carbon_reduction":1280,"energy_saving":860,"green_ratio":42.6,"water_saving":3200},
        "customer_distribution":[
            {"name":"工业","count":7500,"percent":75,"color":"#5ba050"},{"name":"商业","count":1800,"percent":18,"color":"#7ec87b"},
            {"name":"居民","count":700,"percent":7,"color":"#e8a020"},{"name":"其他","count":240,"percent":2.4,"color":"#6e8e5e"}],
        "monthly_benefit":{"power_supply":128,"power_sold":96.8,"loss_rate":8.5,"total_revenue":586,"total_cost":352,"net_profit":234,"unit_cost":0.82,"profit_rate":42.6,"carbon_reduction":1280},
        "hydro_monthly":{"labels":["01","05","10","15","20","25","30","35","40"],"data":[520,680,490,750,440,620,580,710,530]},
        "storage_revenue_monthly":{"labels":["01","05","08","12","15","18","22","25","30"],"discharge":[450,580,720,630,780,650,590,810,700],"revenue":[35,42,58,48,62,55,50,68,54]},
        "consumer_structure":[
            {"name":"IT设备","percent":60,"color":"#5ba050"},{"name":"制冷","percent":22,"color":"#7ec87b"},
            {"name":"照明","percent":10,"color":"#e8a020"},{"name":"其他","percent":8,"color":"#6e8e5e"}]
    })

@app.route('/api/optimize')
def api_optimize():
    return jsonify({"total_cost":12850.5,"total_emission":320.8,"total_efficiency":0.87,"renewable_ratio":0.62})

@app.route('/api/forum')
def api_forum():
    return jsonify({"posts":[
        {"id":1,"author":"管理员","time":"2026-05-05","title":"欢迎使用数据中心综合管理平台","content":"本平台提供检测平台、交流平台、调度模型三大功能模块。","likes":5,"comments":2},
        {"id":2,"author":"学生A","time":"2026-05-05","title":"光伏发电模型参数调整经验分享","content":"在调整光伏模型参数时，需考虑地理位置、天气状况、温度系数等因素。","likes":3,"comments":1},
        {"id":3,"author":"学生B","time":"2026-05-04","title":"关于储能调度策略的思考","content":"储能调度需考虑峰谷电价、电池寿命、荷电状态等多个因素。","likes":4,"comments":3},
        {"id":4,"author":"学生C","time":"2026-05-04","title":"碳排放计算方法汇总","content":"数据中心碳排放主要来自电力消耗。整理了排放因子法、质量平衡法等常用方法。","likes":7,"comments":5},
        {"id":5,"author":"学生D","time":"2026-05-03","title":"风电场选址经验分享","content":"风电场选址需要风速数据、地形数据、电网接入条件。","likes":2,"comments":0},
    ]})
