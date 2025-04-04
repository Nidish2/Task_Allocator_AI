import React from "react";
import {
  ClerkProvider,
  SignIn,
  SignUp,
  SignedIn,
  SignedOut,
  useUser,
} from "@clerk/clerk-react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
  useLocation,
} from "react-router-dom";
import SupervisorDashboard from "./pages/SupervisorDashboard";
import EmployeeDashboard from "./pages/EmployeeDashboard";

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

function PublicPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold text-blue-600 mb-8">
        Welcome to Task Allocation AI
      </h1>
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h2 className="text-xl font-semibold mb-6 text-gray-700">
          Select your role:
        </h2>
        <div className="space-y-4">
          <button
            onClick={() => navigate("/sign-in?role=supervisor")}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors"
          >
            Supervisor Sign In
          </button>
          <button
            onClick={() => navigate("/sign-in?role=employee")}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
          >
            Employee Sign In
          </button>
          <div className="mt-4 text-center">
            <p className="text-gray-600">
              Don't have an account?{" "}
              <a
                href="/sign-up"
                className="text-blue-600 hover:underline"
                onClick={(e) => {
                  e.preventDefault();
                  navigate("/sign-up");
                }}
              >
                Sign Up
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <Router>
        <Routes>
          <Route
            path="/"
            element={
              <>
                <SignedOut>
                  <PublicPage />
                </SignedOut>
                <SignedIn>
                  <RoleRouter />
                </SignedIn>
              </>
            }
          />
          <Route
            path="/sign-in"
            element={
              <SignIn
                routing="path"
                path="/sign-in"
                signUpUrl="/sign-up"
                afterSignInUrl="/role-selection"
              />
            }
          />
          <Route
            path="/sign-up"
            element={
              <SignUp
                routing="path"
                path="/sign-up"
                signInUrl="/sign-in"
                afterSignUpUrl="/role-selection"
              />
            }
          />
          <Route path="/role-selection" element={<RoleSelection />} />

          {/* Protected routes */}
          <Route
            path="/supervisor"
            element={
              <SignedIn>
                <SupervisorDashboard />
              </SignedIn>
            }
          />
          <Route
            path="/employee"
            element={
              <SignedIn>
                <EmployeeDashboard />
              </SignedIn>
            }
          />
        </Routes>
      </Router>
    </ClerkProvider>
  );
}

// Helper component to route based on role parameter
function RoleRouter() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isLoaded } = useUser();

  React.useEffect(() => {
    if (!isLoaded) return;

    // Check if we are already on a role-specific page to prevent redirect loops
    if (
      location.pathname === "/supervisor" ||
      location.pathname === "/employee"
    ) {
      return;
    }

    // Check if role is in query params (for direct navigation)
    const params = new URLSearchParams(location.search);
    const roleParam = params.get("role");

    // First check unsafeMetadata (where we set the role)
    const userRole = user?.unsafeMetadata?.role as string | undefined;

    if (userRole === "supervisor") {
      navigate("/supervisor");
    } else if (userRole === "employee") {
      navigate("/employee");
    } else if (roleParam === "supervisor") {
      navigate("/supervisor");
    } else if (roleParam === "employee") {
      navigate("/employee");
    } else {
      // If no role is set, redirect to role selection
      navigate("/role-selection");
    }
  }, [isLoaded, user, navigate, location]);

  return null; // This component just handles navigation
}

// Role Selection Component
function RoleSelection() {
  const { user } = useUser();
  const navigate = useNavigate();

  const handleRoleSelect = async (role: "supervisor" | "employee") => {
    try {
      // Update unsafeMetadata which is available in the update method
      await user?.update({
        unsafeMetadata: { role },
      });

      // For publicMetadata, use the specific method if needed
      // Note: You may need to implement this separately if required
      // Clerk often restricts publicMetadata updates to backend operations

      // Navigate based on selected role
      navigate(role === "supervisor" ? "/supervisor" : "/employee");
    } catch (error) {
      console.error("Failed to update user role:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h2 className="text-xl font-semibold mb-6 text-center text-gray-700">
          Select your role
        </h2>
        <div className="space-y-4">
          <button
            onClick={() => handleRoleSelect("supervisor")}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors"
          >
            Supervisor
          </button>
          <button
            onClick={() => handleRoleSelect("employee")}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
          >
            Employee
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
