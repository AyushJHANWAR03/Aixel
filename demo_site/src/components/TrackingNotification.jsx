import { useApp } from '../context/AppContext';
import './TrackingNotification.css';

const TrackingNotification = () => {
  const { notification } = useApp();

  return (
    <div className={`tracking-notification ${notification.show ? 'show' : ''}`}>
      {notification.message}
    </div>
  );
};

export default TrackingNotification;
