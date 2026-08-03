import { NavLink } from "react-router-dom";

export default function AppNavigation() {
  return (
    <nav className="app-navigation card">
      <div>
        <p className="eyebrow">PORTSIGNAL</p>
        <strong>Portfolio intelligence</strong>
      </div>

      <div className="navigation-links">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          Dashboard
        </NavLink>

        <NavLink
          to="/analytics"
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          Analytics
        </NavLink>

        <NavLink
          to="/news"
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          News
        </NavLink>
      </div>
    </nav>
  );
}