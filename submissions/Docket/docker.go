package main

import (
	"errors"
	"os/exec"
	"strings"
)

// ListContainers lists all Docker containers (running and stopped).
func ListContainers() ([]map[string]string, error) {
	args := []string{"ps", "--format", "{{.ID}} {{.Names}} {{.Status}}", "-a"}
	out, err := exec.Command("docker", args...).CombinedOutput()
	if err != nil {
		return nil, errors.New(string(out) + ": " + err.Error())
	}

	lines := strings.Split(string(out), "\n")
	var containers []map[string]string
	for _, line := range lines {
		if line == "" {
			continue
		}
		fields := strings.Fields(line)
		status := "stopped"
		if strings.Contains(strings.Join(fields[2:], " "), "Up") {
			status = "running"
		}
		container := map[string]string{
			"ID":     fields[0],
			"Name":   fields[1],
			"Status": status,
		}
		containers = append(containers, container)
	}
	return containers, nil
}


// CreateContainerFromImage creates and starts a new container with port mapping.
func CreateContainerFromImage(image string, name string, hostPort string, containerPort string) (map[string]string, error) {
	cmdArgs := []string{
		"run", "-d", "--name", name,
		"-p", hostPort + ":" + containerPort, // Port mapping
		image,
	}

	out, err := exec.Command("docker", cmdArgs...).CombinedOutput()
	if err != nil {
		return nil, err
	}

	containerID := strings.TrimSpace(string(out))
	container := map[string]string{
		"ID":   containerID,
		"Name": name,
	}
	return container, nil
}


// RunContainer creates and starts a container.
func RunContainer(containerID string) error {
	out, err := exec.Command("docker", "start", containerID).CombinedOutput()
	if err != nil {
		return errors.New("failed to start container: " + string(out))
	}
	return nil
}

// StopContainer stops a running container.
func StopContainer(containerID string) (map[string]string, error) {
	out, err := exec.Command("docker", "stop", containerID).CombinedOutput()
	if err != nil {
		return nil, err
	}

	stoppedContainerID := strings.TrimSpace(string(out))
	container := map[string]string{
		"ID": stoppedContainerID,
	}
	return container, nil
}

// DeleteContainer removes a container (forcefully if needed).
func DeleteContainer(containerID string) (map[string]string, error) {
	args := []string{"rm", "-f"}
	
	args = append(args, containerID)
	out, err := exec.Command("docker", args...).CombinedOutput()
	if err != nil {
		return nil, err
	}

	deletedContainerID := strings.TrimSpace(string(out))
	container := map[string]string{
		"ID": deletedContainerID,
	}
	return container, nil
}

// RenameContainer renames a container.
func RenameContainer(oldName, newName string) error {
	if oldName == "" || newName == "" {
		return errors.New("container names cannot be empty")
	}

	cmd := exec.Command("docker", "rename", oldName, newName)
	out, err := cmd.CombinedOutput()
	if err != nil {
		return errors.New("failed to rename container: " + string(out))
	}

	return nil
}

// ListImages lists all Docker images.
func ListImages() ([]map[string]string, error) {
	args := []string{"images", "--format", "{{.Repository}} {{.Tag}} {{.ID}}"}
	out, err := exec.Command("docker", args...).CombinedOutput()
	if err != nil {
		return nil, err
	}

	lines := strings.Split(string(out), "\n")
	var images []map[string]string
	for _, line := range lines {
		if line == "" {
			continue
		}
		fields := strings.Fields(line)
		image := map[string]string{
			"Repository": fields[0],
			"Tag":        fields[1],
			"ID":         fields[2],
		}
		images = append(images, image)
	}
	return images, nil
}

// DeleteImage removes a Docker image.
func DeleteImage(imageID string) (map[string]string, error) {
	args := []string{"rmi", "-f", imageID}
	out, err := exec.Command("docker", args...).CombinedOutput()
	if err != nil {
		return nil, err
	}

	deletedImageID := strings.TrimSpace(string(out))
	image := map[string]string{
		"ID": deletedImageID,
	}
	return image, nil
}
