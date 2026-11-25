"use client";

import React from "react";
import { createTheme, ThemeProvider, CssBaseline } from "@mui/material";

// Materio Free Color Palette & Typography
export const materioTheme = createTheme({
  palette: {
    primary: {
      main: "#8C57FF", // Materio Signature Purple
      light: "#A379FF",
      dark: "#7E4EE6",
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: "#8A8D93",
      light: "#9FA4AB",
      dark: "#77797E",
      contrastText: "#FFFFFF",
    },
    success: {
      main: "#56CA00", // Materio Vibrant Green
      light: "#6AD01F",
      dark: "#4CB200",
      contrastText: "#FFFFFF",
    },
    error: {
      main: "#FF4C51", // Materio Coral Red
      light: "#FF666A",
      dark: "#E04347",
      contrastText: "#FFFFFF",
    },
    warning: {
      main: "#FFB400", // Materio Amber
      light: "#FFC026",
      dark: "#E09E00",
      contrastText: "#FFFFFF",
    },
    info: {
      main: "#16B1FF", // Materio Sky Blue
      light: "#35BCFF",
      dark: "#139CE0",
      contrastText: "#FFFFFF",
    },
    background: {
      default: "#F4F5FA", // Materio Crisp Light Grey Canvas
      paper: "#FFFFFF",
    },
    text: {
      primary: "rgba(58, 53, 65, 0.87)",
      secondary: "rgba(58, 53, 65, 0.68)",
      disabled: "rgba(58, 53, 65, 0.38)",
    },
    divider: "rgba(58, 53, 65, 0.12)",
  },
  typography: {
    fontFamily: [
      "-apple-system",
      "BlinkMacSystemFont",
      '"Inter"',
      '"Segoe UI"',
      "Roboto",
      "sans-serif",
    ].join(","),
    h5: {
      fontWeight: 700,
      letterSpacing: "0.18px",
    },
    h6: {
      fontWeight: 600,
      letterSpacing: "0.15px",
    },
    subtitle1: {
      letterSpacing: "0.15px",
      fontWeight: 500,
    },
    body1: {
      letterSpacing: "0.15px",
    },
    button: {
      textTransform: "none",
      fontWeight: 600,
      borderRadius: 8,
    },
  },
  shape: {
    borderRadius: 10,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: "0px 4px 18px 0px rgba(58, 53, 65, 0.10)",
          border: "1px solid rgba(58, 53, 65, 0.08)",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: "7px 18px",
          boxShadow: "none",
          "&:hover": {
            boxShadow: "0px 4px 8px 0px rgba(58, 53, 65, 0.14)",
          },
        },
        contained: {
          "&:hover": {
            boxShadow: "0px 4px 10px 0px rgba(58, 53, 65, 0.2)",
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: 12,
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: "#F9FAFC",
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 700,
          color: "rgba(58, 53, 65, 0.75)",
          textTransform: "uppercase",
          fontSize: "0.72rem",
          letterSpacing: "0.5px",
        },
        body: {
          color: "rgba(58, 53, 65, 0.87)",
          fontSize: "0.8125rem",
        },
      },
    },
  },
});

export default function ThemeRegistry({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider theme={materioTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
