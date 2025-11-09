// mapservice/map.go
package mgmmap

import (
	"context"
	"fmt"
	"time"
)

// Tag represents a map tag with its properties
type Tag struct {
	ID        int64     `json:"id"`
	Name      string    `json:"name"`
	Layer     string    `json:"layer"`
	Longitude float64   `json:"longitude"`
	Latitude  float64   `json:"latitude"`
	CreatedAt time.Time `json:"created_at"`
}

// AddTagRequest represents the request to add a new tag
type AddTagRequest struct {
	Name      string  `json:"name"`
	Layer     string  `json:"layer"`
	Longitude float64 `json:"longitude"`
	Latitude  float64 `json:"latitude"`
}

// AddTagResponse represents the response after adding a tag
type AddTagResponse struct {
	Tag Tag `json:"tag"`
}

//encore:api public method=POST path=/tags
func AddTag(ctx context.Context, req *AddTagRequest) (*AddTagResponse, error) {
	// Validate input
	if req.Name == "" || req.Layer == "" {
		return nil, fmt.Errorf("name and layer are required")
	}
	if req.Longitude < -180 || req.Longitude > 180 || req.Latitude < -90 || req.Latitude > 90 {
		return nil, fmt.Errorf("invalid coordinates")
	}

	// Return a static example tag with the provided data
	tag := Tag{
		ID:        999, // Static ID for demo
		Name:      req.Name,
		Layer:     req.Layer,
		Longitude: req.Longitude,
		Latitude:  req.Latitude,
		CreatedAt: time.Now(),
	}

	return &AddTagResponse{Tag: tag}, nil
}

// GetTagsResponse represents the response with all tags for a layer or all layers
type GetTagsResponse struct {
	Tags []Tag `json:"tags"`
}

//encore:api public method=GET path=/tags/:layer
func GetTagsByLayer(ctx context.Context, layer string) (*GetTagsResponse, error) {
	// Static example data
	exampleTags := map[string][]Tag{
		"sports": {
			{
				ID:        1,
				Name:      "Football Field",
				Layer:     "sports",
				Longitude: -86.2950,
				Latitude:  32.3750,
				CreatedAt: time.Now().Add(-24 * time.Hour),
			},
			{
				ID:        2,
				Name:      "Basketball Court",
				Layer:     "sports",
				Longitude: -86.3050,
				Latitude:  32.3650,
				CreatedAt: time.Now().Add(-12 * time.Hour),
			},
		},
		"music": {
			{
				ID:        3,
				Name:      "Concert Hall",
				Layer:     "music",
				Longitude: -86.3000,
				Latitude:  32.3700,
				CreatedAt: time.Now().Add(-48 * time.Hour),
			},
			{
				ID:        4,
				Name:      "Jazz Club",
				Layer:     "music",
				Longitude: -86.2900,
				Latitude:  32.3600,
				CreatedAt: time.Now().Add(-6 * time.Hour),
			},
		},
	}

	// Return tags for the requested layer, or empty list if layer not found
	tags, exists := exampleTags[layer]
	if !exists {
		return &GetTagsResponse{Tags: []Tag{}}, nil
	}
	return &GetTagsResponse{Tags: tags}, nil
}

//encore:api public method=GET path=/tags
func GetAllTags(ctx context.Context) (*GetTagsResponse, error) {
	// Static example data (all tags)
	exampleTags := []Tag{
		{
			ID:        1,
			Name:      "Football Field",
			Layer:     "sports",
			Longitude: -86.2950,
			Latitude:  32.3750,
			CreatedAt: time.Now().Add(-24 * time.Hour),
		},
		{
			ID:        2,
			Name:      "Basketball Court",
			Layer:     "sports",
			Longitude: -86.3050,
			Latitude:  32.3650,
			CreatedAt: time.Now().Add(-12 * time.Hour),
		},
		{
			ID:        3,
			Name:      "Concert Hall",
			Layer:     "music",
			Longitude: -86.3000,
			Latitude:  32.3700,
			CreatedAt: time.Now().Add(-48 * time.Hour),
		},
		{
			ID:        4,
			Name:      "Jazz Club",
			Layer:     "music",
			Longitude: -86.2900,
			Latitude:  32.3600,
			CreatedAt: time.Now().Add(-6 * time.Hour),
		},
	}

	return &GetTagsResponse{Tags: exampleTags}, nil
}

// ClearTagsResponse represents the response for the ClearTags operation
type ClearTagsResponse struct {
	Success bool `json:"success"`
}

//encore:api public method=DELETE path=/tags
func ClearTags(ctx context.Context) (*ClearTagsResponse, error) {
	// Simulate clearing tags (no actual data to clear in this static version)
	return &ClearTagsResponse{Success: true}, nil
}