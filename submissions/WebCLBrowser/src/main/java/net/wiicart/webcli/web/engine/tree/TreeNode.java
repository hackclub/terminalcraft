package net.wiicart.webcli.web.engine.tree;

import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import java.util.HashSet;
import java.util.Set;

@SuppressWarnings("unused")
class TreeNode {

    private final @NotNull String type; // the tag type, like <body> -> "body"

    private @Nullable String className; // The class of the element, if present
    private @Nullable String id; // The id of the element, if present.

    private @NotNull  Set<TreeNode> children;


    private @Nullable TreeNode parent;

    TreeNode(@NotNull String type) {
        this.type = type;
        className = null;
        parent = null;
        children = new HashSet<>();
    }

    boolean isLeaf() {
        return children.isEmpty();
    }

    boolean isRoot() {
        return parent == null;
    }

    @NotNull String getType() {
        return type;
    }

    @Nullable String getClassName() {
        return className;
    }

    void setClassName(@Nullable String className) {
        this.className = className;
    }

    @Nullable TreeNode getParent() {
        return parent;
    }

    void setParent(@Nullable TreeNode parent) {
        this.parent = parent;
    }

    @NotNull Set<TreeNode> getChildren() {
        return children;
    }

    void setChildren(@NotNull Set<TreeNode> children) {
        this.children = new HashSet<>(children);
    }

}
