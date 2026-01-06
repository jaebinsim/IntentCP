(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const setBadge = (ok, text) => {
    const b = $("#healthBadge");
    if (!b) return;
    b.classList.remove("ok", "bad");
    b.classList.add(ok ? "ok" : "bad");
    b.textContent = text;
  };

  // ------------------------------
  // Theme Toggle (Light / Dark / Auto)
  // ------------------------------
  const THEME_KEY = "homemcp_theme"; // "light" | "dark" | "auto"

  const getPreferredTheme = () => {
    const v = (localStorage.getItem(THEME_KEY) || "auto").toLowerCase();
    return v === "light" || v === "dark" || v === "auto" ? v : "auto";
  };

  const applyTheme = (mode) => {
    // mode: "light" | "dark" | "auto"
    const body = document.body;
    if (!body) return;

    if (mode === "auto") {
      // Remove manual overrides to fall back to OS preference (prefers-color-scheme)
      body.removeAttribute("data-theme");
    } else {
      body.setAttribute("data-theme", mode);
    }
  };

  const themeLabel = (mode) => {
    if (mode === "light") return "☀️ Light";
    if (mode === "dark") return "🌙 Dark";
    return "🖥️ Auto";
  };

  const nextTheme = (mode) => {
    if (mode === "auto") return "light";
    if (mode === "light") return "dark";
    return "auto";
  };

  // Watch OS theme changes (only matters when mode === "auto")
  const mq = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  let osWatcherAttached = false;

  const attachOsWatcher = () => {
    if (!mq || osWatcherAttached) return;
    osWatcherAttached = true;

    const handler = () => {
      const mode = getPreferredTheme();
      if (mode !== "auto") return;
      // If we're in auto, ensure overrides are cleared and label stays correct.
      applyTheme("auto");
      const btn = document.getElementById("themeToggle");
      if (btn) btn.textContent = themeLabel("auto");
    };

    // Safari < 14 uses addListener/removeListener
    if (typeof mq.addEventListener === "function") {
      mq.addEventListener("change", handler);
    } else if (typeof mq.addListener === "function") {
      mq.addListener(handler);
    }
  };

  const bootThemeToggle = () => {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;

    // Prevent duplicate listeners if bootThemeToggle is called multiple times
    if (btn.dataset.initialized === "1") {
      // Still ensure current preference is applied
      applyTheme(getPreferredTheme());
      return;
    }
    btn.dataset.initialized = "1";

    // Apply saved preference (default: auto)
    let mode = getPreferredTheme();
    applyTheme(mode);
    btn.textContent = themeLabel(mode);

    // React to OS changes when in Auto
    attachOsWatcher();

    btn.addEventListener("click", () => {
      mode = nextTheme(mode);
      localStorage.setItem(THEME_KEY, mode);
      applyTheme(mode);
      btn.textContent = themeLabel(mode);
    });
  };

  const checkHealth = async () => {
    try {
      const res = await fetch("/health/", { cache: "no-store" });
      if (!res.ok) throw new Error("health http " + res.status);
      setBadge(true, "healthy");
    } catch (_e) {
      setBadge(false, "unhealthy");
    }
  };

  const tryFetchJson = async (url, opts) => {
    const res = await fetch(url, opts);
    let data = null;
    try {
      data = await res.json();
    } catch (_e) {}
    return { ok: res.ok, status: res.status, data };
  };

  const callTuya = async (device, cmd) => {
    // Prefer POST, fallback to GET (some early implementations used GET)
    const url = `/tuya/${encodeURIComponent(device)}/${encodeURIComponent(cmd)}`;

    let r = await tryFetchJson(url, { method: "POST" });
    if (!r.ok && (r.status === 405 || r.status === 404)) {
      r = await tryFetchJson(url, { method: "GET" });
    }
    return r;
  };

  const bootOverview = async () => {
    bootThemeToggle();
    await checkHealth();
  };

  const bootSettings = async () => {
    bootThemeToggle();
    await checkHealth();
    const ta = $("textarea[name='toml_text']");
    if (!ta) return;
    const initial = ta.value;
    window.addEventListener("beforeunload", (e) => {
      if (ta.value !== initial) {
        e.preventDefault();
        e.returnValue = "";
      }
    });
  };

  const bootDevices = async () => {
    bootThemeToggle();
    await checkHealth();

    const ta = $("textarea[name='toml_text']");
    if (ta) {
      const initial = ta.value;
      window.addEventListener("beforeunload", (e) => {
        if (ta.value !== initial) {
          e.preventDefault();
          e.returnValue = "";
        }
      });
    }

    // quick action buttons
    $$("button[data-action='tuya']").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const device = btn.dataset.device;
        const cmd = btn.dataset.cmd;
        const resEl = $("#res-" + device);
        if (resEl) resEl.textContent = "calling…";
        btn.disabled = true;

        try {
          const r = await callTuya(device, cmd);
          const txt = r.data ? JSON.stringify(r.data) : `(http ${r.status})`;
          if (resEl) resEl.textContent = txt;
        } catch (_e) {
          if (resEl) resEl.textContent = "error";
        } finally {
          btn.disabled = false;
        }
      });
    });

    const hintBtn = $("#btnFormatHint");
    if (hintBtn && ta) {
      hintBtn.addEventListener("click", () => {
        const example = `# Example devices.toml\n\n[devices.living_light]\nkind = "switch"\ntuya_on_device_id = "..."\ntuya_off_device_id = "..."\n\n[devices.subdesk_light]\nkind = "dimmer"\ntuya_device_id = "..."\n`;
        alert(example);
      });
    }
  };

  window.IntentCP = {
    bootOverview,
    bootSettings,
    bootDevices,
  };
})();
