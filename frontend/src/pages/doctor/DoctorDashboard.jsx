import { useEffect, useState } from "react";
import { Icon, RecentReferralsPanel, useApp } from "../../components/PrototypeApp.jsx";
import { authService } from "../../services/authService.js";

export default function DashboardPage({ user }) {
  const { t } = useApp();
  const [referrals, setReferrals] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
  async function fetchData() {
    try {
      setLoading(true);
      setError(null);

      // هر دو API را همزمان بگیر
      const [patientsData, referralsData] = await Promise.all([
        authService.doctorPatients(),
        authService.doctorReferrals(),
      ]);

      setPatients(patientsData.patients || []);
      setReferrals(referralsData.referrals || []);
    } catch (err) {
      console.error(err);
      setError(err.message || "خطا در دریافت اطلاعات");
    } finally {
      setLoading(false);
    }
  }
  fetchData();
}, []);

  // آمار بر اساس بیماران
  const stats = [
    {
      key: 'total',
      label: t('totalVisits'),
      value: patients.length,
      sub: t('thisMonth'),
      icon: 'file',
      tone: 'teal',
      foot: 'up',
    },
    {
      key: 'waiting',
      label: t('waitingReview'),
      value: referrals.filter(r => r.status === 'pending').length,
      sub: t('inQueue'),
      icon: 'clock',
      tone: 'amber',
      foot: 'warn',
    },
    {
      key: 'accepted',
      label: t('accepted'),
      value: referrals.filter(r => r.status === 'accepted').length,
      sub: t('completed'),
      icon: 'check',
      tone: 'mint',
      foot: 'up',
    },
    {
      key: 'today',
      label: t('today'),
      value: patients.filter(p => {
        if (!p.last_referral_date) return false;
        const d = new Date(p.last_referral_date);
        const today = new Date();
        return d.toDateString() === today.toDateString();
      }).length,
      sub: t('todayAppointments'),
      icon: 'calendar',
      tone: 'dark',
      foot: 'neutral',
    },
  ];

  if (loading) {
    return (
      <div className="page">
        <div className="page-head">
          <div className="page-head-left">
            <h1>{t('doctorDashboard')}</h1>
            <p>در حال بارگذاری...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <div className="page-head">
          <div className="page-head-left">
            <h1>{t('doctorDashboard')}</h1>
            <p style={{ color: 'red' }}>خطا: {error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-head">
        <div className="page-head-left">
          <h1>
            {user.role === 'doctor' ? t('doctorDashboard')
              : user.role === 'admission' ? t('admissionDashboard')
              : t('adminDashboard')}
          </h1>
          <p>
            {user.role === 'doctor' ? t('doctorSubtitle')
              : user.role === 'admission' ? t('admissionSubtitle')
              : t('adminSubtitle')}
          </p>
        </div>
      </div>

      <div className="stat-grid">
        {stats.map(s => (
          <div key={s.key} className="stat-card">
            <div className="stat-head">
              <div className={`stat-icon ${s.tone}`}>
                <Icon name={s.icon} size={22} stroke={2.2} />
              </div>
            </div>
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
            <div className={`stat-foot ${s.foot}`}>{s.sub}</div>
          </div>
        ))}
      </div>

      <RecentReferralsPanel referrals={referrals} />
    </div>
  );
}