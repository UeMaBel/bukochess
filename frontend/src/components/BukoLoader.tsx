import "../styles/BukoLoader.css";

export const BukoLoader = () => {
  return (
    <div className="spinner-container">
      <div className="buko-spinner"></div>
      <span className="loading-text">BUKO THINKING...</span>
    </div>
  );
};
