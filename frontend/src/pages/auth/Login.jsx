import { useEffect, useState } from 'react';
import { Icon, PreviewCard, TogglesInline, useApp } from '../../components/PrototypeApp.jsx';
import { authService } from '../../services/authService.js';

export default function Login({ onLogin, showToast }) {
  const { t } = useApp();
  const [id, setId] = useState('');
  const [pwd, setPwd] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [remember, setRemember] = useState(true);
  const [errs, setErrs] = useState({});
  const [loading, setLoading] = useState(false);

  // یک بار هنگام باز شدن صفحه، CSRF توکن بگیر
  useEffect(() => {
    authService.getCsrf();
  }, []);

  const submit = async (event) => {
    event.preventDefault();
    const errors = {};

    if (!id.trim()) errors.id = t('errIdReq');
    else if (!/^\d{10}$/.test(id)) errors.id = t('errIdLen');
    if (!pwd.trim()) errors.pwd = t('errPwdReq');

    if (Object.keys(errors).length) {
      setErrs(errors);
      return;
    }

    setLoading(true);
    setErrs({});

    try {
      const result = await authService.login(id, pwd);
        
      const user = {
        ...result.user,
        fullName: `${result.user.first_name} ${result.user.last_name}`.trim(),
        fullNameEn: `${result.user.first_name} ${result.user.last_name}`.trim(),
        role: result.user.role === 'reception' ? 'admission' : result.user.role,
      };
    
      sessionStorage.setItem('csrf_token', result.csrf_token);
      showToast(result.message, 'success');
    
      // ─── سوپرادمین → فقط ادمین جنگو، بدون onLogin ───
      if (result.user.is_superuser && result.redirect_url?.startsWith('/admin/')) {
        window.location.href = `http://localhost:8000${result.redirect_url}`;
        return;
      }
    
      // ─── بقیه نقش‌ها → داشبورد React ───
      onLogin(user);
    
      if (result.redirect_url) {
        window.location.href = result.redirect_url;
      }
    } catch (error) {
      const message = error.message || t('errCreds');
      setErrs({ general: message });
      showToast(message, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-shell">
      <aside className="photo-side">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="photo-inner">
          <div className="hero-pill"><span className="hero-pill-dot" />{t('sidePill')}</div>
          <div className="hero-heading">
            <h2>{t('sideTitle1')}<br /><span className="grad">{t('sideTitle2')}</span></h2>
            <p>{t('sideSubtitle')}</p>
          </div>
          <PreviewCard />
          <div className="hero-features">
            <Feature icon="zap" text={t('sideFeat1')} tone="hf-1" />
            <Feature icon="shield" text={t('sideFeat2')} tone="hf-2" />
            <Feature icon="trending" text={t('sideFeat3')} tone="hf-3" />
          </div>
        </div>
      </aside>

      <section className="form-side">
        <div className="form-head">
          <div className="brand-mark">
            <div className="brand-mark-icon"><Icon name="pulse" size={22} stroke={2.5} /></div>
            <div className="brand-mark-text">
              <span className="brand-mark-name">{t('brandShort')}</span>
              <span className="brand-mark-sub">{t('brandSub')}</span>
            </div>
          </div>
          <TogglesInline />
        </div>

        <div className="form-body"><div className="form-inner">
          <div className="form-eyebrow"><span className="form-eyebrow-dot" />{t('welcomeEyebrow')}</div>
          <h1 className="form-title">{t('welcome')} <span className="form-title-wave">👋</span></h1>
          <p className="form-sub">{t('loginSub')}</p>

          <form onSubmit={submit} noValidate>
            <Field label={t('nationalId')} error={errs.id}>
              <div className="fld-wrap">
                <input
                  type="text"
                  value={id}
                  onChange={(event) => {
                    setId(event.target.value.replace(/\D/g, ''));
                    if (errs.id) setErrs((current) => ({ ...current, id: '' }));
                  }}
                  placeholder="1234567890"
                  maxLength={10}
                  className={errs.id ? 'err' : ''}
                />
                <span className="fld-icon-l"><Icon name="user" size={18} /></span>
              </div>
            </Field>

            <Field label={t('password')} error={errs.pwd}>
              <div className="fld-wrap">
                <input
                  type={showPwd ? 'text' : 'password'}
                  value={pwd}
                  onChange={(event) => {
                    setPwd(event.target.value);
                    if (errs.pwd) setErrs((current) => ({ ...current, pwd: '' }));
                  }}
                  placeholder="••••••••"
                  className={errs.pwd ? 'err' : ''}
                />
                <span className="fld-icon-l"><Icon name="lock" size={18} /></span>
                <button type="button" className="fld-icon-r" onClick={() => setShowPwd(!showPwd)}>
                  <Icon name={showPwd ? 'eyeOff' : 'eye'} size={18} />
                </button>
              </div>
            </Field>

            <div className="checkbox-row">
              <label className="checkbox">
                <input type="checkbox" checked={remember} onChange={() => setRemember(!remember)} />
                <span className="checkbox-box">{remember && <Icon name="check" size={13} stroke={3.5} />}</span>
                <span>{t('rememberMe')}</span>
              </label>
              <button type="button" className="forgot-link">{t('forgotPassword')}</button>
            </div>

            <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%' }} disabled={loading}>
              {loading ? <><span className="sp" />{t('loggingIn')}</> : <>{t('loginBtn')}<Icon name="arrow" size={18} stroke={2.5} /></>}
            </button>

            {errs.general && <div className="fld-err" style={{ marginTop: 18 }}><Icon name="alert" size={14} stroke={2.5} />{errs.general}</div>}
          </form>
        </div></div>

        <footer className="form-foot"><span>{t('version')}</span><span>{t('copyright')}</span></footer>
      </section>
    </div>
  );
}

function Feature({ icon, text, tone }) {
  return (
    <div className="hero-feature">
      <div className={`hero-feature-icon ${tone}`}><Icon name={icon} size={14} stroke={2.5} /></div>
      <span>{text}</span>
    </div>
  );
}

function Field({ label, error, children }) {
  return (
    <div className="fld">
      <label className="fld-label">{label}</label>
      {children}
      {error && <div className="fld-err"><Icon name="alert" size={12} stroke={2.5} />{error}</div>}
    </div>
  );
}