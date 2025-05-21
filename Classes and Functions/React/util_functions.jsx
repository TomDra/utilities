
// Fetching API data
import axios from "axios";
import React, { useState, useEffect } from "react";
const [apiData, setApiData] = useState({});
const [loading, setLoading] = useState(true);
const fetchApiData = async () => {
    try {
        const response = await axios.get(`${API_URL}/apiEndpoint`);
        setAPIdata(response.data);
        setLoading(false);
    } catch (error) {
        console.error("Error fetching API data:", error);
    }
};
useEffect(() => {
    fetchApiData();
}, []);



// Legend for charts and tables:
const Legend = ({ labels, colors }) => (
    <Box sx={{ mb: 2 }}>
        <Box
            component="ul"
            sx={{
                listStyleType: "none",
                p: 0,
                display: "flex",
                gap: 2,
                flexWrap: "wrap",
            }}
        >
            {labels.map((label, index) => (
                <Box
                    component="li"
                    key={index}
                    sx={{ display: "flex", alignItems: "center", gap: 1 }}
                >
                    <Box
                        sx={{
                            width: 12,
                            height: 12,
                            backgroundColor: colors[index],
                            borderRadius: "50%",
                        }}
                    />
                    <Typography variant="body2">{label}</Typography>
                </Box>
            ))}
        </Box>
    </Box>
);
