function deleteTable(table_id) {
    fetch("/deletetable", {
      method: "POST",
      body: JSON.stringify({ table_id: table_id }),
    }).then((_res) => {
      window.location.href = "/view";
    });
  }