def get_clock_html(minutes_to_midnight: float, theme: str = "dark") -> str:
    minutes_to_midnight = max(0.1, float(minutes_to_midnight))

    # 0 min => ponteiro quase “meia-noite”
    minute_hand_position = 60 - minutes_to_midnight
    minute_rotation = minute_hand_position * 6

    # tema
    if theme == "light":
        bg = "#f6f7fb"
        card = "#ffffff"
        dial = "#f2f2f2"
        text = "#0f172a"
        sub = "#475569"
        marker = "#94a3b8"
        marker_strong = "#334155"
        accent = "#ef4444"
        glow = "rgba(239,68,68,0.25)"
    else:
        bg = "#0b0f16"
        card = "#0f1624"
        dial = "#161a22"
        text = "#e5e7eb"
        sub = "#94a3b8"
        marker = "#3b4658"
        marker_strong = "#9aa4b2"
        accent = "#ff3b30"
        glow = "rgba(255,59,48,0.25)"

    html = f"""
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

        :root {{
          --bg: {bg};
          --card: {card};
          --dial: {dial};
          --text: {text};
          --sub: {sub};
          --marker: {marker};
          --marker-strong: {marker_strong};
          --accent: {accent};
          --glow: {glow};
        }}

        body {{
          margin: 0;
          background: transparent;
          font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
          display:flex;
          justify-content:center;
          align-items:center;
        }}

        .panel {{
          width: 520px;
          padding: 24px 24px 18px;
          border-radius: 18px;
          background: radial-gradient(1200px 600px at 50% 0%, rgba(255,255,255,0.04), transparent 45%),
                      var(--card);
          box-shadow: 0 16px 50px rgba(0,0,0,0.45);
          border: 1px solid rgba(255,255,255,0.06);
          text-align:center;
        }}

        .title {{
          color: var(--text);
          font-weight: 900;
          letter-spacing: 1px;
          font-size: 22px;
          margin: 0 0 6px;
        }}

        .subtitle {{
          color: var(--sub);
          font-size: 12px;
          letter-spacing: 2px;
          text-transform: uppercase;
          margin: 0 0 18px;
        }}

        .clock-wrap {{
          display:flex;
          justify-content:center;
          align-items:center;
          padding: 6px 0 12px;
        }}

        .clock {{
          width: 320px;
          height: 320px;
          border-radius: 50%;
          position: relative;
          background: radial-gradient(circle at 35% 30%, rgba(255,255,255,0.08), transparent 42%),
                      radial-gradient(circle at 50% 60%, rgba(0,0,0,0.35), transparent 60%),
                      var(--dial);
          border: 8px solid rgba(0,0,0,0.55);
          box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06), 0 24px 60px rgba(0,0,0,0.5);
        }}

        .marker {{
          position:absolute;
          top:50%;
          left:50%;
          width:2px;
          height:10px;
          background: var(--marker);
          border-radius: 2px;
          transform-origin:center center;
        }}

        .marker.hour {{
          width:4px;
          height:18px;
          background: var(--marker-strong);
        }}

        .marker.danger {{
          background: var(--accent);
          box-shadow: 0 0 10px var(--glow);
        }}

        .hand {{
          position:absolute;
          left:50%;
          bottom:50%;
          transform-origin: bottom center;
          border-radius: 8px;
        }}

        .hour-hand {{
          width:6px;height:72px;
          background: var(--text);
          opacity: 0.22;
          margin-left:-3px;
          transform: rotate(320deg);
        }}

        .minute-hand {{
          width:5px;height:112px;
          background: var(--text);
          margin-left:-2.5px;
          box-shadow: 0 0 14px rgba(0,0,0,0.35);
          transition: transform 1.2s cubic-bezier(0.2, 1.4, 0.2, 1);
          z-index: 5;
        }}

        .second-hand {{
          width:2px;height:128px;
          background: var(--accent);
          margin-left:-1px;
          opacity: 0.9;
          z-index: 6;
        }}

        .center {{
          position:absolute;
          top:50%;left:50%;
          width:14px;height:14px;
          transform: translate(-50%,-50%);
          background: var(--accent);
          border-radius:50%;
          box-shadow: 0 0 18px rgba(0,0,0,0.7);
          z-index: 10;
        }}

        .readout {{
          position:absolute;
          left:50%;
          top:67%;
          transform: translateX(-50%);
          font-size: 30px;
          font-weight: 900;
          letter-spacing: 1px;
          color: var(--accent);
          text-shadow: 0 0 14px var(--glow);
        }}

        .label {{
          position:absolute;
          left:50%;
          top:78%;
          transform: translateX(-50%);
          font-size: 10px;
          letter-spacing: 2px;
          text-transform: uppercase;
          color: var(--sub);
        }}

        /* digital abaixo */
        #MyClockDisplay {{
          margin-top: 14px;
          color: var(--accent);
          font-size: 44px;
          font-family: Orbitron, monospace;
          letter-spacing: 6px;
          text-shadow: 0 0 18px var(--glow);
        }}

        .digital-sub {{
          margin-top: 4px;
          color: var(--sub);
          font-size: 11px;
          letter-spacing: 2px;
          text-transform: uppercase;
        }}
      </style>
    </head>
    <body>
      <div class="panel">
        <h1 class="title">DOOMSDAY CLOCK AI</h1>
        <p class="subtitle">SISTEMA DE MONITORAMENTO DE RISCO EXISTENCIAL</p>

        <div class="clock-wrap">
          <div class="clock" id="clock">
            <div class="hand hour-hand"></div>
            <div class="hand minute-hand" id="minute"></div>
            <div class="hand second-hand" id="second"></div>
            <div class="center"></div>

            <div class="readout">{minutes_to_midnight:.1f} MIN</div>
            <div class="label">TO MIDNIGHT</div>
          </div>
        </div>

        <div id="MyClockDisplay" onload="showTime()"></div>
        <div class="digital-sub">LOCAL TIME</div>
      </div>

      <script>
        const clock = document.getElementById("clock");

        for (let i = 0; i < 60; i++) {{
          const m = document.createElement("div");
          m.classList.add("marker");
          if (i % 5 === 0) m.classList.add("hour");
          if (i >= 45) m.classList.add("danger"); // zona vermelha
          const radius = 145;
          m.style.transform = `translate(-50%, -50%) rotate(${{i*6}}deg) translateY(-${{radius}}px)`;
          clock.appendChild(m);
        }}

        const riskDeg = {minute_rotation};
        setTimeout(() => {{
          document.getElementById("minute").style.transform = `rotate(${{riskDeg}}deg)`;
        }}, 120);

        function animateSeconds() {{
          const now = new Date();
          const s = now.getSeconds();
          const ms = now.getMilliseconds();
          const deg = ((s + ms/1000) / 60) * 360;
          document.getElementById("second").style.transform = `rotate(${{deg}}deg)`;
          requestAnimationFrame(animateSeconds);
        }}
        animateSeconds();

        function showTime(){{
          const date = new Date();
          let h = date.getHours();
          let m = date.getMinutes();
          let s = date.getSeconds();
          let session = "AM";
          if(h === 0) h = 12;
          if(h > 12) {{ h = h - 12; session = "PM"; }}
          h = (h < 10) ? "0"+h : h;
          m = (m < 10) ? "0"+m : m;
          s = (s < 10) ? "0"+s : s;
          const time = h + ":" + m + ":" + s + " " + session;
          const el = document.getElementById("MyClockDisplay");
          el.textContent = time;
          setTimeout(showTime, 1000);
        }}
        showTime();
      </script>
    </body>
    </html>
    """
    return html