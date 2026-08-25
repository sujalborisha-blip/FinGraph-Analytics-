import React, { useEffect, useRef, useState } from "react";
import { Network } from "vis-network/standalone";

function GraphView() {
  const [graphData, setGraphData] = useState({
    nodes: [],
    links: []
  });

  const [selectedNode, setSelectedNode] = useState(null);

  const networkRef = useRef(null);
  const containerRef = useRef(null);

  // Fetch graph data from backend
  const fetchGraph = () => {
    fetch("http://localhost:4000/graph")
      .then(res => res.json())
      .then(data => {
        setGraphData(data);
      })
      .catch(error => {
        console.error("Error loading graph:", error);
      });
  };

  // Load graph when page opens
  useEffect(() => {
    fetchGraph();
  }, []);

  // Create / update graph
  useEffect(() => {
    if (!containerRef.current || graphData.nodes.length === 0) {
      return;
    }

    const data = {
      nodes: graphData.nodes.map(node => ({
        id: node.id,
        label: node.id
      })),

      edges: graphData.links.map(link => ({
        from: link.source,
        to: link.target
      }))
    };

    const options = {
      nodes: {
        shape: "circle",
        color: "lightblue",
        size: 25,
        font: {
          size: 16
        }
      },

      edges: {
        color: "gray",
        arrows: "to",
        width: 2
      },

      physics: {
        enabled: true
      },

      interaction: {
        hover: true,
        navigationButtons: true,
        zoomView: true
      }
    };

    networkRef.current = new Network(
      containerRef.current,
      data,
      options
    );

    // Node selection
    networkRef.current.on("selectNode", params => {
      if (params.nodes.length > 0) {
        setSelectedNode(params.nodes[0]);
      }
    });

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
      }
    };
  }, [graphData]);

  // Refresh button
  const handleRefresh = () => {
    fetchGraph();
  };

  // Fit graph button
  const handleFit = () => {
    if (networkRef.current) {
      networkRef.current.fit({
        animation: true
      });
    }
  };

  // Clear selection button
  const handleClear = () => {
    if (networkRef.current) {
      networkRef.current.unselectAll();
    }

    setSelectedNode(null);
  };

  return (
    <div className="graph-section">

      <div className="graph-toolbar">

        <button onClick={handleRefresh}>
          🔄 Refresh Graph
        </button>

        <button onClick={handleFit}>
          ⛶ Fit Graph
        </button>

        <button onClick={handleClear}>
          ✕ Clear Selection
        </button>

      </div>

      <div className="graph-status">
        {selectedNode
          ? `Selected Node: ${selectedNode}`
          : "Select a node to investigate"}
      </div>

      <div
        ref={containerRef}
        className="graph-container"
      />

    </div>
  );
}

export default GraphView;