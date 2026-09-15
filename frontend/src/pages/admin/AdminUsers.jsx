import { useEffect, useState } from 'react';
import { useApp } from "../../components/PrototypeApp.jsx";
import { authService } from '../../services/authService.js';

export default function AdminUsers() {
  const { t, lang } = useApp();
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    authService.adminDoctors()
      .then(setDoctors)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page">در حال بارگذاری...</div>;
  if (error) return <div className="page">{error}</div>;

  return (
    <div className="page">
      <div className="page-head">
        <div className="page-head-left">
          <h1>{t('doctorsList')}</h1>
          <p>{t('doctorsSubtitle')}</p>
        </div>
      </div>
      <div className="doctor-grid">
        {doctors.map((d) => (
          <div key={d.id} className="doctor-card">
            <div className="doctor-head">
              <div>
                <div className="doctor-name">{d.user.first_name} {d.user.last_name}</div>
                <div className="doctor-specialty">{d.specialty}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}